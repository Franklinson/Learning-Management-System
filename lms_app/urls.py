from django.urls import path, include
from . import views

urlpatterns = [
    # Authentication URLs
    path('accounts/', include('django.contrib.auth.urls')), # Provides login, logout, password change urls
    path('accounts/register/', views.RegisterView.as_view(), name='register'),
    path('accounts/profile/', views.profile_view, name='profile'),


    # Course URLs
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('courses/create/', views.CourseCreateView.as_view(), name='course_create'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('courses/<int:pk>/update/', views.CourseUpdateView.as_view(), name='course_update'),
    path('courses/<int:pk>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),

    # Lesson URLs
    path('courses/<int:course_pk>/lessons/create/', views.LessonCreateView.as_view(), name='lesson_create'),
    path('lessons/<int:pk>/', views.LessonDetailView.as_view(), name='lesson_detail'),
    path('lessons/<int:pk>/update/', views.LessonUpdateView.as_view(), name='lesson_update'),
    path('lessons/<int:pk>/delete/', views.LessonDeleteView.as_view(), name='lesson_delete'),

    # Quiz URLs
    path('lessons/<int:lesson_pk>/quiz/create/', views.QuizCreateView.as_view(), name='quiz_create'),
    path('quiz/<int:pk>/', views.QuizDetailView.as_view(), name='quiz_detail'),
    path('quiz/<int:pk>/update/', views.QuizUpdateView.as_view(), name='quiz_update'),
    path('quiz/<int:pk>/delete/', views.QuizDeleteView.as_view(), name='quiz_delete'),

    # Question URLs
    path('quiz/<int:quiz_pk>/questions/create/', views.QuestionCreateView.as_view(), name='question_create'),
    path('questions/<int:pk>/update/', views.QuestionUpdateView.as_view(), name='question_update'),
    path('questions/<int:pk>/delete/', views.QuestionDeleteView.as_view(), name='question_delete'),

    # Answer URLs
    path('questions/<int:question_pk>/answers/create/', views.AnswerCreateView.as_view(), name='answer_create'),
    path('answers/<int:pk>/update/', views.AnswerUpdateView.as_view(), name='answer_update'),
    path('answers/<int:pk>/delete/', views.AnswerDeleteView.as_view(), name='answer_delete'),

    # Enrollment and Progress URLs
    path('courses/<int:course_pk>/enroll/', views.EnrollCourseView.as_view(), name='enroll_course'),
    path('enrollments/', views.EnrollmentListView.as_view(), name='enrollment_list'),
    path('lessons/<int:pk>/mark_completed/', views.MarkLessonCompletedView.as_view(), name='mark_lesson_completed'),
    path('quiz/<int:pk>/take/', views.TakeQuizView.as_view(), name='take_quiz'),
    path('quiz/attempt/<int:pk>/results/', views.QuizAttemptDetailView.as_view(), name='quiz_attempt_results'),
]
