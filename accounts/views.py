from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm
from .models import SubjectType

from django.shortcuts import render
from django.contrib.auth.decorators import login_required


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


@login_required
def profile_view(request):
    teacher_links = (
        SubjectType.objects
        .select_related("subject")
        .filter(user=request.user, role="teacher")
    )
    student_links = (
        SubjectType.objects
        .select_related("subject")
        .filter(user=request.user, role="student")
    )

    teacher_subjects = [st.subject for st in teacher_links]
    student_subjects = [st.subject for st in student_links]

    return render(
        request,
        "accounts/profile.html",
        {
            "teacher_subjects": teacher_subjects,
            "student_subjects": student_subjects,
            "is_teacher": getattr(request.user, "is_teacher", False),
            "is_student": getattr(request.user, "is_student", False),
        },
    )
