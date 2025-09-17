from django.urls import path, include
from . import views

urlpatterns = [
    # Authentication URLs
    path('accounts/', include('django.contrib.auth.urls')), # Provides login, logout, password change urls
    path('accounts/register/', views.RegisterView.as_view(), name='register'),
    path('accounts/profile/', views.profile_view, name='profile'),


    # Course URLs
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path(\'courses/create/\', views.CourseCreateView.as_view(), name=\'course_create\'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('courses/<int:pk>/update/', views.CourseUpdateView.as_view(), name='course_update'),
    path('courses/<int:pk>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),

    # Lesson URLs
    path('courses/<int:course_pk>/lessons/create/', views.LessonCreateView.as_view(), name='lesson_create'),
    path('lessons/<int:pk>/', views.LessonDetailView.as_view(), name='lesson_detail'),
    path('lessons/<int:pk>/update/', views.LessonUpdateView.as_view(), name='lesson_update'),
    path('lessons/<int:pk>/delete/', views.LessonDeleteView.as_view(), name='lesson_delete'),
]
