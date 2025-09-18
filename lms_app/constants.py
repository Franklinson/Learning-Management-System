"""Constants used throughout the LMS application."""

# User roles
STUDENT_ROLE = 'student'
INSTRUCTOR_ROLE = 'instructor'

USER_ROLES = [
    (STUDENT_ROLE, 'Student'),
    (INSTRUCTOR_ROLE, 'Instructor'),
]

# Messages
MESSAGES = {
    'ENROLLMENT_SUCCESS': 'Successfully enrolled in {course_title}!',
    'ALREADY_ENROLLED': 'You are already enrolled in {course_title}.',
    'LESSON_COMPLETED': "Lesson '{lesson_title}' marked as completed.",
    'LESSON_ALREADY_COMPLETED': "Lesson '{lesson_title}' was already marked as completed.",
    'QUIZ_COMPLETED': 'Quiz completed! Your score: {score}/{total}.',
    'PERMISSION_DENIED': 'You do not have permission to access this page.',
    'STUDENT_ONLY': 'Only students can access this page.',
    'INSTRUCTOR_ONLY': 'Only instructors can access this page.',
}

# Template paths
TEMPLATES = {
    'BASE': 'lms_app/base.html',
    'COURSE_LIST': 'lms_app/course_list.html',
    'COURSE_DETAIL': 'lms_app/course_detail.html',
    'COURSE_FORM': 'lms_app/course_form.html',
    'LESSON_DETAIL': 'lms_app/lesson_detail.html',
    'QUIZ_DETAIL': 'lms_app/quiz_detail.html',
    'TAKE_QUIZ': 'lms_app/take_quiz.html',
    'QUIZ_RESULTS': 'lms_app/quiz_attempt_results.html',
    'REGISTER': 'registration/register.html',
    'LOGIN': 'registration/login.html',
}

# URL names
URLS = {
    'COURSE_LIST': 'course_list',
    'COURSE_DETAIL': 'course_detail',
    'LESSON_DETAIL': 'lesson_detail',
    'QUIZ_DETAIL': 'quiz_detail',
    'TAKE_QUIZ': 'take_quiz',
    'LOGIN': 'login',
    'PROFILE': 'profile',
}