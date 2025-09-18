from django.urls import reverse_lazy, reverse
from django.views.generic import (
    CreateView, ListView, DetailView, UpdateView, DeleteView, View
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages

from .models import Course, Lesson, User, Quiz, Question, Answer, Enrollment, LessonProgress, QuizAttempt
from .forms import UserRegisterForm, QuizForm, QuestionForm, AnswerForm, TakeQuizForm
from .mixins import InstructorOrSuperuserRequiredMixin, StudentRequiredMixin, CourseOwnerMixin
from .services import EnrollmentService, LessonService, QuizService


# User Authentication Views
class RegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Account created for {self.object.username}! You can now log in.')
        return response

def profile_view(request):
    return render(request, 'lms_app/profile.html')


# Course Views
class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'lms_app/course_list.html'
    context_object_name = 'courses'


class CourseCreateView(InstructorOrSuperuserRequiredMixin, CreateView):
    model = Course
    fields = ['title', 'description']
    template_name = 'lms_app/course_form.html'
    success_url = reverse_lazy('course_list')

    def form_valid(self, form):
        form.instance.instructor = self.request.user
        return super().form_valid(form)


class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'lms_app/course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        user = self.request.user

        context['is_enrolled'] = False
        context['enrollment'] = None
        context['lesson_progress'] = {}

        if user.is_authenticated and user.role == 'student':
            enrollment = Enrollment.objects.filter(student=user, course=course).first()
            if enrollment:
                context['is_enrolled'] = True
                context['enrollment'] = enrollment
                # Get progress for each lesson
                for lesson in course.lessons.all():
                    lesson_progress = LessonProgress.objects.filter(enrollment=enrollment, lesson=lesson).first()
                    context['lesson_progress'][lesson.pk] = lesson_progress.completed if lesson_progress else False

        return context


class CourseUpdateView(InstructorOrSuperuserRequiredMixin, CourseOwnerMixin, UpdateView):
    model = Course
    fields = ['title', 'description']
    template_name = 'lms_app/course_form.html'

    def get_success_url(self):
        return reverse_lazy('course_detail', kwargs={'pk': self.object.pk})


class CourseDeleteView(InstructorOrSuperuserRequiredMixin, CourseOwnerMixin, DeleteView):
    model = Course
    template_name = 'lms_app/course_confirm_delete.html'
    success_url = reverse_lazy('course_list')


# Lesson Views
class LessonCreateView(InstructorOrSuperuserRequiredMixin, CreateView):
    model = Lesson
    fields = ['title', 'content', 'order']
    template_name = 'lms_app/lesson_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, pk=kwargs['course_pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.course = self.course
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('course_detail', kwargs={'pk': self.course.pk})

    def test_func(self):
        if not super().test_func():
            return False
        self.course = get_object_or_404(Course, pk=self.kwargs['course_pk'])
        return self.course.instructor == self.request.user or self.request.user.is_superuser


class LessonDetailView(LoginRequiredMixin, DetailView):
    model = Lesson
    template_name = 'lms_app/lesson_detail.html'
    context_object_name = 'lesson'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.get_object()
        user = self.request.user

        context['can_mark_completed'] = False
        context['is_completed'] = False
        context['quiz_attempted'] = False
        context['latest_quiz_score'] = None

        if user.is_authenticated and user.role == 'student':
            enrollment = Enrollment.objects.filter(student=user, course=lesson.course).first()
            if enrollment:
                lesson_progress = LessonProgress.objects.filter(enrollment=enrollment, lesson=lesson).first()
                if lesson_progress:
                    context['is_completed'] = lesson_progress.completed

                # Check if lesson can be marked completed (if user is enrolled and not an instructor)
                if not user.role == 'instructor' and enrollment:
                    context['can_mark_completed'] = True

                # Check quiz attempt for this lesson if a quiz exists
                if hasattr(lesson, 'quiz'):
                    quiz_attempt = QuizAttempt.objects.filter(student=user, quiz=lesson.quiz).order_by('-date_attempted').first()
                    if quiz_attempt:
                        context['quiz_attempted'] = True
                        context['latest_quiz_score'] = quiz_attempt.score

        return context


class LessonUpdateView(InstructorOrSuperuserRequiredMixin, UpdateView):
    model = Lesson
    fields = ['title', 'content', 'order']
    template_name = 'lms_app/lesson_form.html'

    def get_success_url(self):
        return reverse_lazy('lesson_detail', kwargs={'pk': self.object.pk})

    def test_func(self):
        if not super().test_func():
            return False
        lesson = self.get_object()
        return lesson.course.instructor == self.request.user or self.request.user.is_superuser


class LessonDeleteView(InstructorOrSuperuserRequiredMixin, DeleteView):
    model = Lesson
    template_name = 'lms_app/lesson_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('course_detail', kwargs={'pk': self.object.course.pk})

    def test_func(self):
        if not super().test_func():
            return False
        lesson = self.get_object()
        return lesson.course.instructor == self.request.user or self.request.user.is_superuser


# Quiz Views
class QuizCreateView(InstructorOrSuperuserRequiredMixin, CreateView):
    model = Quiz
    form_class = QuizForm
    template_name = 'lms_app/quiz_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.lesson = get_object_or_404(Lesson, pk=kwargs['lesson_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lesson'] = self.lesson
        return context

    def form_valid(self, form):
        # Ensure only one quiz per lesson
        if hasattr(self.lesson, 'quiz'):
            messages.error(self.request, f"A quiz already exists for lesson: {self.lesson.title}.")
            return redirect(reverse_lazy('lesson_detail', kwargs={'pk': self.lesson.pk}))

        form.instance.lesson = self.lesson
        messages.success(self.request, "Quiz created successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('quiz_detail', kwargs={'pk': self.object.pk})

    def test_func(self):
        if not super().test_func():
            return False
        self.lesson = get_object_or_404(Lesson, pk=self.kwargs['lesson_pk'])
        return self.lesson.course.instructor == self.request.user or self.request.user.is_superuser


class QuizDetailView(LoginRequiredMixin, DetailView):
    model = Quiz
    template_name = 'lms_app/quiz_detail.html'
    context_object_name = 'quiz'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        quiz = self.get_object()

        context['is_student_enrolled'] = False
        context['has_attempted_quiz'] = False
        context['latest_attempt_score'] = None

        if user.is_authenticated and user.role == 'student':
            enrollment = Enrollment.objects.filter(student=user, course=quiz.lesson.course).first()
            if enrollment:
                context['is_student_enrolled'] = True
                latest_attempt = QuizAttempt.objects.filter(student=user, quiz=quiz).order_by('-date_attempted').first()
                if latest_attempt:
                    context['has_attempted_quiz'] = True
                    context['latest_attempt_score'] = latest_attempt.score
        return context


class QuizUpdateView(InstructorOrSuperuserRequiredMixin, UpdateView):
    model = Quiz
    form_class = QuizForm
    template_name = 'lms_app/quiz_form.html'

    def get_success_url(self):
        return reverse_lazy('quiz_detail', kwargs={'pk': self.object.pk})

    def test_func(self):
        if not super().test_func():
            return False
        quiz = self.get_object()
        return quiz.lesson.course.instructor == self.request.user or self.request.user.is_superuser


class QuizDeleteView(InstructorOrSuperuserRequiredMixin, DeleteView):
    model = Quiz
    template_name = 'lms_app/quiz_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('lesson_detail', kwargs={'pk': self.object.lesson.pk})

    def test_func(self):
        if not super().test_func():
            return False
        quiz = self.get_object()
        return quiz.lesson.course.instructor == self.request.user or self.request.user.is_superuser


# Question Views
class QuestionCreateView(InstructorOrSuperuserRequiredMixin, CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'lms_app/question_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.quiz = get_object_or_404(Quiz, pk=kwargs['quiz_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quiz'] = self.quiz
        return context

    def form_valid(self, form):
        form.instance.quiz = self.quiz
        messages.success(self.request, "Question added successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('quiz_detail', kwargs={'pk': self.quiz.pk})

    def test_func(self):
        if not super().test_func():
            return False
        self.quiz = get_object_or_404(Quiz, pk=self.kwargs['quiz_pk'])
        return self.quiz.lesson.course.instructor == self.request.user or self.request.user.is_superuser


class QuestionUpdateView(InstructorOrSuperuserRequiredMixin, UpdateView):
    model = Question
    form_class = QuestionForm
    template_name = 'lms_app/question_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quiz'] = self.get_object().quiz
        return context

    def get_success_url(self):
        return reverse_lazy('quiz_detail', kwargs={'pk': self.object.quiz.pk})

    def test_func(self):
        if not super().test_func():
            return False
        question = self.get_object()
        return question.quiz.lesson.course.instructor == self.request.user or self.request.user.is_superuser


class QuestionDeleteView(InstructorOrSuperuserRequiredMixin, DeleteView):
    model = Question
    template_name = 'lms_app/question_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('quiz_detail', kwargs={'pk': self.object.quiz.pk})

    def test_func(self):
        if not super().test_func():
            return False
        question = self.get_object()
        return question.quiz.lesson.course.instructor == self.request.user or self.request.user.is_superuser


# Answer Views
class AnswerCreateView(InstructorOrSuperuserRequiredMixin, CreateView):
    model = Answer
    form_class = AnswerForm
    template_name = 'lms_app/answer_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.question = get_object_or_404(Question, pk=kwargs['question_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question'] = self.question
        return context

    def form_valid(self, form):
        form.instance.question = self.question
        messages.success(self.request, "Answer added successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('quiz_detail', kwargs={'pk': self.question.quiz.pk})

    def test_func(self):
        if not super().test_func():
            return False
        self.question = get_object_or_404(Question, pk=self.kwargs['question_pk'])
        return self.question.quiz.lesson.course.instructor == self.request.user or self.request.user.is_superuser


class AnswerUpdateView(InstructorOrSuperuserRequiredMixin, UpdateView):
    model = Answer
    form_class = AnswerForm
    template_name = 'lms_app/answer_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question'] = self.get_object().question
        return context

    def get_success_url(self):
        return reverse_lazy('quiz_detail', kwargs={'pk': self.object.question.quiz.pk})

    def test_func(self):
        if not super().test_func():
            return False
        answer = self.get_object()
        return answer.question.quiz.lesson.course.instructor == self.request.user or self.request.user.is_superuser


class AnswerDeleteView(InstructorOrSuperuserRequiredMixin, DeleteView):
    model = Answer
    template_name = 'lms_app/answer_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('quiz_detail', kwargs={'pk': self.object.question.quiz.pk})

    def test_func(self):
        if not super().test_func():
            return False
        answer = self.get_object()
        return answer.question.quiz.lesson.course.instructor == self.request.user or self.request.user.is_superuser


# Student Enrollment and Progress Views
class EnrollCourseView(StudentRequiredMixin, View):
    def post(self, request, course_pk):
        course = get_object_or_404(Course, pk=course_pk)
        enrollment, created = EnrollmentService.enroll_student(request.user, course)
        
        if created:
            messages.success(request, f"Successfully enrolled in {course.title}!")
        else:
            messages.info(request, f"You are already enrolled in {course.title}.")
        
        return redirect(reverse_lazy('course_detail', kwargs={'pk': course_pk}))


class EnrollmentListView(LoginRequiredMixin, ListView):
    model = Enrollment
    template_name = 'lms_app/enrollment_list.html'
    context_object_name = 'enrollments'

    def get_queryset(self):
        if self.request.user.role == 'student':
            return Enrollment.objects.filter(student=self.request.user).select_related('course')
        # Instructors/Admins could see all enrollments, or only for their courses
        # For now, let's limit to student's own enrollments
        messages.error(self.request, "Only students can view their enrollments.")
        return Enrollment.objects.none() # Return empty queryset for non-students


class MarkLessonCompletedView(StudentRequiredMixin, View):
    def post(self, request, pk):
        lesson = get_object_or_404(Lesson, pk=pk)
        lesson_progress, created = LessonService.mark_lesson_completed(request.user, lesson)
        
        if created or not lesson_progress.completed:
            messages.success(request, f"Lesson '{lesson.title}' marked as completed.")
        else:
            messages.info(request, f"Lesson '{lesson.title}' was already marked as completed.")
        
        return redirect(reverse_lazy('lesson_detail', kwargs={'pk': pk}))


class TakeQuizView(LoginRequiredMixin, View):
    template_name = 'lms_app/take_quiz.html'

    def dispatch(self, request, *args, **kwargs):
        self.quiz = get_object_or_404(Quiz, pk=kwargs['pk'])
        self.lesson = self.quiz.lesson
        self.course = self.lesson.course

        if request.user.role != 'student':
            messages.error(request, "Only students can take quizzes.")
            return redirect(reverse_lazy('quiz_detail', kwargs={'pk': self.quiz.pk}))

        self.enrollment = Enrollment.objects.filter(student=request.user, course=self.course).first()
        if not self.enrollment:
            messages.error(request, f"You must be enrolled in '{self.course.title}' to take this quiz.")
            return redirect(reverse_lazy('quiz_detail', kwargs={'pk': self.quiz.pk}))

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        form = TakeQuizForm(quiz=self.quiz)
        context = {
            'quiz': self.quiz,
            'lesson': self.lesson,
            'course': self.course,
            'form': form,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        form = TakeQuizForm(request.POST, quiz=self.quiz)
        if form.is_valid():
            score, total_questions = QuizService.calculate_quiz_score(self.quiz, form.cleaned_data)
            quiz_attempt = QuizService.record_quiz_attempt(request.user, self.quiz, score)
            
            messages.success(request, f"Quiz completed! Your score: {score}/{total_questions}.")
            return redirect(reverse_lazy('quiz_attempt_results', kwargs={'pk': quiz_attempt.pk}))
        else:
            context = {
                'quiz': self.quiz,
                'lesson': self.lesson,
                'course': self.course,
                'form': form,
            }
            return render(request, self.template_name, context)


class QuizAttemptDetailView(LoginRequiredMixin, DetailView):
    model = QuizAttempt
    template_name = 'lms_app/quiz_attempt_results.html'
    context_object_name = 'attempt'

    def test_func(self):
        # Only the student who made the attempt or a superuser/instructor can view results
        attempt = self.get_object()
        return self.request.user == attempt.student or \
               self.request.user.is_superuser or \
               (self.request.user.role == 'instructor' and self.request.user == attempt.quiz.lesson.course.instructor)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()  # Redirect to login
        else:
            messages.error(self.request, "You do not have permission to view these quiz results.")
            return redirect(reverse_lazy('profile')) # Or some other appropriate redirect


# Reporting Views
class ReportingDashboardView(InstructorOrSuperuserRequiredMixin, ListView):
    model = Course
    template_name = 'lms_app/reporting_dashboard.html'
    context_object_name = 'courses'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Course.objects.all().order_by('title')
        elif self.request.user.role == 'instructor':
            return Course.objects.filter(instructor=self.request.user).order_by('title')
        return Course.objects.none() # Should be caught by mixin, but good for safety

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_courses = context['courses'] # This is the filtered queryset from get_queryset

        course_data = []
        for course in all_courses:
            total_students_enrolled = course.enrollments.filter(course=course).count()
            lessons_in_course = course.lessons.count()

            students_progress = []
            for enrollment in course.enrollments.all():
                student = enrollment.student
                completed_lessons = LessonProgress.objects.filter(enrollment=enrollment, completed=True).count()

                # Calculate quiz attempts and average score
                quiz_attempts = QuizAttempt.objects.filter(student=student, quiz__lesson__course=course)
                total_quiz_score = sum([attempt.score for attempt in quiz_attempts])

                total_possible_quiz_score = 0
                for lesson in course.lessons.all():
                    if hasattr(lesson, 'quiz'):
                        total_possible_quiz_score += lesson.quiz.questions.count() # Assuming 1 point per question

                average_quiz_score = (total_quiz_score / total_possible_quiz_score) * 100 if total_possible_quiz_score > 0 else 0

                students_progress.append({
                    'student': student,
                    'completed_lessons': completed_lessons,
                    'total_lessons': lessons_in_course,
                    'lesson_completion_percentage': (completed_lessons / lessons_in_course * 100) if lessons_in_course > 0 else 0,
                    'average_quiz_score': average_quiz_score
                })

            course_data.append({
                'course': course,
                'total_students_enrolled': total_students_enrolled,
                'students_progress': students_progress,
            })
        context['course_data'] = course_data
        return context
