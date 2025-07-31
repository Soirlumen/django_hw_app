from django.urls import path
from .views import SignUpView, dashboard_view, profile_view

urlpatterns = [
    #path("signup/", SignUpView.as_view(), name="signup"),
    path("", dashboard_view, name="dashboard"),
    path("accounts/", profile_view, name="profile"),
]
