from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ("student", "Student"),
        ("instructor", "Instructor"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student")

    def __str__(self):
        return f"{self.username} ({self.role})"


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="courses_taught",
        limit_choices_to={"role": "instructor"},
    )

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.IntegerField()

    class Meta:
        ordering = ["order"]
        unique_together = ["course", "order"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


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

    class Meta:
        unique_together = ["student", "course"]

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"


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

    def __str__(self):
        return f"{self.student.username}'s attempt on {self.quiz.title} (Score: {self.score})"
