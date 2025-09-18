from django.db.models import Count, Avg
from .models import Course, Enrollment, LessonProgress, QuizAttempt


class ReportingUtils:
    """Utility functions for generating reports and analytics."""
    
    @staticmethod
    def get_course_analytics(course):
        """Get comprehensive analytics for a course."""
        total_students = course.enrollments.count()
        total_lessons = course.lessons.count()
        
        # Calculate completion rates
        completed_lessons_data = LessonProgress.objects.filter(
            lesson__course=course, completed=True
        ).values('enrollment').annotate(completed_count=Count('lesson'))
        
        completion_rates = []
        for enrollment in course.enrollments.all():
            completed = completed_lessons_data.filter(enrollment=enrollment.pk).first()
            completed_count = completed['completed_count'] if completed else 0
            completion_rate = (completed_count / total_lessons * 100) if total_lessons > 0 else 0
            completion_rates.append(completion_rate)
        
        avg_completion_rate = sum(completion_rates) / len(completion_rates) if completion_rates else 0
        
        # Quiz analytics
        quiz_attempts = QuizAttempt.objects.filter(quiz__lesson__course=course)
        avg_quiz_score = quiz_attempts.aggregate(avg_score=Avg('score'))['avg_score'] or 0
        
        return {
            'total_students': total_students,
            'total_lessons': total_lessons,
            'avg_completion_rate': avg_completion_rate,
            'avg_quiz_score': avg_quiz_score,
            'total_quiz_attempts': quiz_attempts.count()
        }
    
    @staticmethod
    def get_student_dashboard_data(student):
        """Get dashboard data for a student."""
        enrollments = Enrollment.objects.filter(student=student).select_related('course')
        
        dashboard_data = []
        for enrollment in enrollments:
            course = enrollment.course
            total_lessons = course.lessons.count()
            completed_lessons = LessonProgress.objects.filter(
                enrollment=enrollment, completed=True
            ).count()
            
            recent_quiz_attempts = QuizAttempt.objects.filter(
                student=student, quiz__lesson__course=course
            ).order_by('-date_attempted')[:3]
            
            dashboard_data.append({
                'course': course,
                'enrollment': enrollment,
                'total_lessons': total_lessons,
                'completed_lessons': completed_lessons,
                'completion_percentage': (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0,
                'recent_quiz_attempts': recent_quiz_attempts
            })
        
        return dashboard_data