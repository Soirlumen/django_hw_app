from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm
from .models import StudentProfile, TeacherProfile

from django.shortcuts import render
from django.contrib.auth.decorators import login_required


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


@login_required
def dashboard_view(request):
    return render(request, "dashboard.html")


@login_required
def profile_view(request):
    user_stus_info = StudentProfile.objects.filter(user=request.user).first()
    user_teac_info = TeacherProfile.objects.filter(user=request.user).first()
    return render(
        request,
        "accounts/profile.html",
        {
            "user_stus_info": user_stus_info,
            "user_teac_info": user_teac_info,
        },
    )
