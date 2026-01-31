from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

@login_required
def profile_view(request):
    return render(
        request,
        "accounts/profile.html",
        {
            "teacher_subjects": request.user.teacher_subjects,
            "student_subjects": request.user.student_subjects,
            "is_teacher": request.user.is_teacher,
            "is_student": request.user.is_student,
        },
    )

@login_required
def dashboard_view(request):
    return render(request, "dashboard.html")
