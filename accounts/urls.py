from django.urls import path
from .views import dashboard_view, profile_view, SignUpView

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("", dashboard_view, name="dashboard"),
    path("accounts/", profile_view, name="profile"),
]
