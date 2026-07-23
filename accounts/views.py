from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm, EmailChangeForm,TelChangeForm
from news.models import NewsPost
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
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
    edit_mode = request.GET.get("edit")
    form = None
    if edit_mode == "email":
        form_class = EmailChangeForm
    elif edit_mode == "tel":
        form_class = TelChangeForm
    else:
        form_class = None

    if form_class:
        form = form_class(
            request.POST or None,
            instance=request.user,
        )

        if request.method == "POST" and form.is_valid():
            form.save()
            messages.success(
                request,
                _("Údaj byl úspěšně změněn."),
            )
            return redirect("profile")

    return render(
        request,
        "accounts/profile.html",
        {
            "teacher_subjects": request.user.teacher_subjects,
            "student_subjects": request.user.student_subjects,
            "is_teacher": request.user.is_teacher,
            "is_student": request.user.is_student,
            "edit_mode": edit_mode,
            "form": form,
        },
    )

@login_required
def dashboard_view(request):
    three_posts=NewsPost.objects.order_by("-date")[:3]
    return render(request, "dashboard.html",{"posts":three_posts})

