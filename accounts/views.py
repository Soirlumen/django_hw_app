from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm
from news.models import NewsPost
from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def success_login_view(request):
    return render(request, "accounts/success_login.html")

class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True
    def get_success_url(self):
        return reverse_lazy("success_login")

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
    three_posts=NewsPost.objects.order_by("-date")[:3]
    return render(request, "dashboard.html",{"posts":three_posts})

