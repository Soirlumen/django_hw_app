from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES=[
        ('student','Student'),
        ('teacher','teacher'),
        ('admin','Admin'),
    ]
    role=models.CharField(max_length=10,choices=ROLE_CHOICES,default='student')

    def is_teacher(self):
        return self.role=='teacher'
    def is_student(self):
        return self.role=="student"
    def is_admin(self):
        return self.role=='admin'
    

class StudentProfile(models.Model):
    user=models.OneToOneField('accounts.CustomUser', on_delete=models.CASCADE, related_name='student_profile')
    year=models.PositiveSmallIntegerField(null=True)
    field_of_study=models.CharField(max_length=100, null=True)
    def __str__(self):
        return f"{self.user.username} (student)"
    
class TeacherProfile(models.Model):
    user=models.OneToOneField('accounts.CustomUser', on_delete=models.CASCADE, related_name='teacher_profile')
    department=models.CharField(max_length=100, null=True)
    subjects=models.CharField(max_length=50, null=True)
    def __str__(self):
        return f"{self.user.username} (teacher)"