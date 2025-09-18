from django.db import models
from django.contrib.auth.models import AbstractUser
from .constants import USER_ROLES, STUDENT_ROLE

class User(AbstractUser):
    role = models.CharField(max_length=10, choices=USER_ROLES, default=STUDENT_ROLE)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Course(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField()
    instructor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="courses_taught",
        limit_choices_to={"role": "instructor"},
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()  # Default manager
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['instructor']),
        ]

    def __str__(self):
        return f"{self.title} (by {self.instructor.username})"


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200, db_index=True)
    content = models.TextField()
    order = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]
        unique_together = ["course", "order"]
        indexes = [
            models.Index(fields=['course', 'order']),
        ]

    def __str__(self):
        return f"{self.order}. {self.title} ({self.course.title})"


class Quiz(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name="quiz")
    title = models.CharField(max_length=200)

    def __str__(self):
        return f"Quiz for {self.lesson.title}"


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()

    def __str__(self):
        return f"Q: {self.text[:50]}..."


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"A: {self.text[:50]}... ({'Correct' if self.is_correct else 'Incorrect'})"


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollments", limit_choices_to={"role": "student"})
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    date_enrolled = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()  # Default manager
    
    class Meta:
        unique_together = ["student", "course"]
        ordering = ['-date_enrolled']
        indexes = [
            models.Index(fields=['student', 'course']),
            models.Index(fields=['date_enrolled']),
        ]

    def __str__(self):
        return f"{self.student.username} → {self.course.title}"


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="lesson_progress")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="progress")
    completed = models.BooleanField(default=False)
    date_completed = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ["enrollment", "lesson"]

    def __str__(self):
        return f"{self.enrollment.student.username}'s progress in {self.lesson.title}"


class QuizAttempt(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quiz_attempts", limit_choices_to={"role": "student"})
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    score = models.IntegerField(default=0)
    date_attempted = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()  # Default manager
    
    class Meta:
        ordering = ['-date_attempted']
        indexes = [
            models.Index(fields=['student', 'quiz']),
            models.Index(fields=['date_attempted']),
        ]

    def __str__(self):
        return f"{self.student.username} → {self.quiz.title} ({self.score}pts)"
    
    @property
    def percentage_score(self):
        """Calculate percentage score based on total questions."""
        total_questions = self.quiz.questions.count()
        return (self.score / total_questions * 100) if total_questions > 0 else 0
