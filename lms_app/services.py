from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Enrollment, LessonProgress, QuizAttempt, Course, Lesson, Quiz, Answer


class EnrollmentService:
    """Service for handling enrollment-related business logic."""
    
    @staticmethod
    def enroll_student(student, course):
        """Enroll a student in a course if not already enrolled."""
        enrollment, created = Enrollment.objects.get_or_create(
            student=student, course=course
        )
        return enrollment, created
    
    @staticmethod
    def get_student_progress(enrollment):
        """Get progress data for a student's enrollment."""
        completed_lessons = LessonProgress.objects.filter(
            enrollment=enrollment, completed=True
        ).count()
        total_lessons = enrollment.course.lessons.count()
        
        return {
            'completed_lessons': completed_lessons,
            'total_lessons': total_lessons,
            'completion_percentage': (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        }


class LessonService:
    """Service for handling lesson-related business logic."""
    
    @staticmethod
    def mark_lesson_completed(student, lesson):
        """Mark a lesson as completed for a student."""
        enrollment = get_object_or_404(Enrollment, student=student, course=lesson.course)
        
        lesson_progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson,
            defaults={'completed': True, 'date_completed': timezone.now()}
        )
        
        if not created and not lesson_progress.completed:
            lesson_progress.completed = True
            lesson_progress.date_completed = timezone.now()
            lesson_progress.save()
        
        return lesson_progress, created


class QuizService:
    """Service for handling quiz-related business logic."""
    
    @staticmethod
    def calculate_quiz_score(quiz, answers_data):
        """Calculate score for a quiz attempt."""
        score = 0
        total_questions = quiz.questions.count()
        
        for question in quiz.questions.all():
            selected_answer_id = answers_data.get(f'question_{question.pk}')
            if selected_answer_id:
                selected_answer = get_object_or_404(Answer, pk=selected_answer_id)
                if selected_answer.is_correct:
                    score += 1
        
        return score, total_questions
    
    @staticmethod
    def record_quiz_attempt(student, quiz, score):
        """Record a quiz attempt."""
        return QuizAttempt.objects.create(
            student=student,
            quiz=quiz,
            score=score
        )