from django.urls import path
from .views import (
    UserLoginView,
    UserLogoutView,
    DashboardView,
    UserCreateView
)

urlpatterns = [
    path("", UserLoginView.as_view(), name="login"), 
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("users/create/", UserCreateView.as_view(), name="user-create"),
]
