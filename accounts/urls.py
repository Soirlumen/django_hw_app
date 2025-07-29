from django.urls import path
from .views import SignUpView, dashboard_view
urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("", dashboard_view, name="dashboard"),
    ]
