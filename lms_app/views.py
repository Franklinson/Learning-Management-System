from django.urls import reverse_lazy, reverse
from django.views.generic import (
    CreateView, ListView, DetailView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseForbidden
from django.contrib import messages
from .models import Course, Lesson, User, Quiz, Question, Answer
from .forms import UserRegisterForm, QuizForm, QuestionForm, AnswerForm


# Mixin for instructor or superuser access
class InstructorOrSuperuserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.role == 'instructor' or self.request.user.is_superuser)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()  # Redirect to login
        else:
            return HttpResponseForbidden("You do not have permission to access this page.")


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


class CourseUpdateView(InstructorOrSuperuserRequiredMixin, UpdateView):
    model = Course
    fields = ['title', 'description']
    template_name = 'lms_app/course_form.html'

    def get_success_url(self):
        return reverse_lazy('course_detail', kwargs={'pk': self.object.pk})

    def test_func(self):
        # First, ensure the user is an instructor or superuser
        if not super().test_func():
            return False
        # Then, ensure they are the instructor of this specific course, or a superuser
        course = self.get_object()
        return course.instructor == self.request.user or self.request.user.is_superuser


class CourseDeleteView(InstructorOrSuperuserRequiredMixin, DeleteView):
    model = Course
    template_name = 'lms_app/course_confirm_delete.html'
    success_url = reverse_lazy('course_list')

    def test_func(self):
        # First, ensure the user is an instructor or superuser
        if not super().test_func():
            return False
        # Then, ensure they are the instructor of this specific course, or a superuser
        course = self.get_object()
        return course.instructor == self.request.user or self.request.user.is_superuser


# Lesson Views
class LessonCreateView(InstructorOrSuperuserRequiredMixin, CreateView):
    model = Lesson
    fields = ['title', 'content', 'order']
    template_name = 'lms_app/lesson_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Get the course based on the course_pk from the URL
        self.course = get_object_or_404(Course, pk=kwargs['course_pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.course = self.course
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('course_detail', kwargs={'pk': self.course.pk})

    def test_func(self):
        # First, ensure the user is an instructor or superuser
        if not super().test_func():
            return False
        # Then, ensure they are the instructor of the course to which the lesson will be added, or a superuser
        return self.course.instructor == self.request.user or self.request.user.is_superuser


class LessonDetailView(LoginRequiredMixin, DetailView):
    model = Lesson
    template_name = 'lms_app/lesson_detail.html'
    context_object_name = 'lesson'


class LessonUpdateView(InstructorOrSuperuserRequiredMixin, UpdateView):
    model = Lesson
    fields = ['title', 'content', 'order']
    template_name = 'lms_app/lesson_form.html'

    def get_success_url(self):
        return reverse_lazy('lesson_detail', kwargs={'pk': self.object.pk})

    def test_func(self):
        # First, ensure the user is an instructor or superuser
        if not super().test_func():
            return False
        # Then, ensure they are the instructor of the course to which the lesson belongs, or a superuser
        lesson = self.get_object()
        return lesson.course.instructor == self.request.user or self.request.user.is_superuser


class LessonDeleteView(InstructorOrSuperuserRequiredMixin, DeleteView):
    model = Lesson
    template_name = 'lms_app/lesson_confirm_delete.html'

    def get_success_url(self):
        # After deleting a lesson, redirect to the course detail page
        return reverse_lazy('course_detail', kwargs={'pk': self.object.course.pk})

    def test_func(self):
        # First, ensure the user is an instructor or superuser
        if not super().test_func():
            return False
        # Then, ensure they are the instructor of the course to which the lesson belongs, or a superuser
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

    def form_valid(self, form):
        form.instance.lesson = self.lesson
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('lesson_detail', kwargs={'pk': self.lesson.pk})

    def test_func(self):
        if not super().test_func():
            return False
        self.lesson = get_object_or_404(Lesson, pk=self.kwargs['lesson_pk'])
        return self.lesson.course.instructor == self.request.user or self.request.user.is_superuser


class QuizDetailView(LoginRequiredMixin, DetailView):
    model = Quiz
    template_name = 'lms_app/quiz_detail.html'
    context_object_name = 'quiz'


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

    def form_valid(self, form):
        form.instance.quiz = self.quiz
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

    def form_valid(self, form):
        form.instance.question = self.question
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


# Quiz Views
class QuizCreateView(InstructorOrSuperuserRequiredMixin, CreateView):
    model = Quiz
    form_class = QuizForm
    template_name = 'lms_app/quiz_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.lesson = get_object_or_404(Lesson, pk=kwargs['lesson_pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.lesson = self.lesson
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('lesson_detail', kwargs={'pk': self.lesson.pk})

    def test_func(self):
        if not super().test_func():
            return False
        self.lesson = get_object_or_404(Lesson, pk=self.kwargs['lesson_pk'])
        return self.lesson.course.instructor == self.request.user or self.request.user.is_superuser


class QuizDetailView(LoginRequiredMixin, DetailView):
    model = Quiz
    template_name = 'lms_app/quiz_detail.html'
    context_object_name = 'quiz'


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

    def form_valid(self, form):
        form.instance.quiz = self.quiz
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

    def form_valid(self, form):
        form.instance.question = self.question
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
