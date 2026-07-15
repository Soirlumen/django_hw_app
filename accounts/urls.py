from django.urls import path
from .views import dashboard_view, profile_view, SignUpView, success_login_view

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("", dashboard_view, name="dashboard"),
    path("profile/", profile_view, name="profile"),
    path("accounts/success_login/", success_login_view, name="success_login")
]
