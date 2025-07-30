from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm
from .models import StudentProfile, TeacherProfile

from django.shortcuts import render, get
from django.contrib.auth.decorators import login_required

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = "registration/signup.html"

@login_required
def dashboard_view(request):
    return render(request, "dashboard.html")

""" @login_required
def profile_view(request):
    user_stus_info=StudentProfile.objects.filter(user=request.user).first()
    user_teac_info=TeacherProfile.objects.filter(user=request.user).first()
    if user_stus_info:
        
         """
        
        
        
        
""" 
    elif hasattr(request.user, 'student_profile'):
        already_submitted = False
        submitted_homework = None
        key = Key.objects.filter(student=request.user, assignment=assignment).first() # nebo get, je to divný
        if key:
            submitted_homework = Homework.objects.filter(key=key).first()
            already_submitted = submitted_homework is not None

        return render(request, "homework/student_detail.html", {
            "hwdetail": assignment,
            "already_submitted": already_submitted,
            "submitted_homework": submitted_homework,
        })

    return HttpResponseForbidden("Nemáš přístup.") 
    
    class StudentProfile(models.Model):
    user=models.OneToOneField('accounts.CustomUser', on_delete=models.CASCADE, related_name='student_profile')
    year=models.PositiveSmallIntegerField(null=True)
    subjects=models.ManyToManyField('hw.Subject',related_name='students')
    field_of_study=models.CharField(max_length=100, null=True)
    def __str__(self):
        return f"{self.user.username} (student)"
    
class TeacherProfile(models.Model):
    user=models.OneToOneField('accounts.CustomUser', on_delete=models.CASCADE, related_name='teacher_profile')
    department=models.CharField(max_length=100, null=True)
    subjects=models.ManyToManyField('hw.Subject',related_name='teachers')
    def __str__(self):
        return f"{self.user.username} (teacher)"
    

    
    
    """