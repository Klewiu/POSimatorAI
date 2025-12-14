from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy

from .models import User
from .forms import UserCreateForm


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        # dostęp dla admina (is_staff) lub superusera
        return self.request.user.is_staff or self.request.user.is_superuser

    def handle_no_permission(self):
        from django.shortcuts import redirect
        return redirect('login')
class UserLoginView(LoginView):
    template_name = "users/login.html"

class UserLogoutView(LogoutView):
    pass

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "users/dashboard.html"

class UserCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = "users/create_user.html"
    success_url = reverse_lazy("estimations")
