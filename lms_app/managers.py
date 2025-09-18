"""Custom model managers for the LMS application."""

from django.db import models
from django.db.models import Count, Avg, Q
from .constants import STUDENT_ROLE, INSTRUCTOR_ROLE


class CourseManager(models.Manager):
    """Custom manager for Course model."""
    
    def with_enrollment_count(self):
        """Annotate courses with enrollment count."""
        return self.annotate(enrollment_count=Count('enrollments'))
    
    def by_instructor(self, instructor):
        """Get courses by instructor."""
        return self.filter(instructor=instructor)
    
    def with_lessons(self):
        """Prefetch related lessons."""
        return self.prefetch_related('lessons')


class EnrollmentManager(models.Manager):
    """Custom manager for Enrollment model."""
    
    def for_student(self, student):
        """Get enrollments for a specific student."""
        return self.filter(student=student).select_related('course')
    
    def for_course(self, course):
        """Get enrollments for a specific course."""
        return self.filter(course=course).select_related('student')
    
    def with_progress(self):
        """Prefetch lesson progress data."""
        return self.prefetch_related('lesson_progress')


class QuizAttemptManager(models.Manager):
    """Custom manager for QuizAttempt model."""
    
    def for_student(self, student):
        """Get quiz attempts for a specific student."""
        return self.filter(student=student).select_related('quiz')
    
    def for_quiz(self, quiz):
        """Get attempts for a specific quiz."""
        return self.filter(quiz=quiz).select_related('student')
    
    def latest_attempts(self):
        """Get latest attempts ordered by date."""
        return self.order_by('-date_attempted')
    
    def with_scores(self):
        """Annotate with score statistics."""
        return self.aggregate(
            avg_score=Avg('score'),
            max_score=models.Max('score'),
            min_score=models.Min('score'),
            total_attempts=Count('id')
        )