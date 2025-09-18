from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import HttpResponseForbidden


class InstructorOrSuperuserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin for views that require instructor or superuser access."""
    
    def test_func(self):
        return (self.request.user.is_authenticated and 
                (self.request.user.role == 'instructor' or self.request.user.is_superuser))

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You do not have permission to access this page.")
        return HttpResponseForbidden("You do not have permission to access this page.")


class StudentRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin for views that require student access."""
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'student'

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "Only students can access this page.")
        return HttpResponseForbidden("Only students can access this page.")


class CourseOwnerMixin(UserPassesTestMixin):
    """Mixin to check if user owns the course."""
    
    def test_func(self):
        course = self.get_object()
        return course.instructor == self.request.user or self.request.user.is_superuser