from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("teacher", "Teacher"),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student")
    first_name=models.CharField(max_length=50,null=True)
    surname=models.CharField(max_length=50,null=True)
    tel=models.PositiveIntegerField(null=True)
    def is_teacher(self):
        return self.role == "teacher"

    def is_student(self):
        return self.role == "student"



class StudentProfile(models.Model):
    user = models.OneToOneField(
        "accounts.CustomUser", on_delete=models.CASCADE, related_name="student_profile"
    )
    year = models.PositiveSmallIntegerField(null=True)
    subjects = models.ManyToManyField("hw.Subject", related_name="students")
    field_of_study = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"{self.user.username} (student)"


class TeacherProfile(models.Model):
    user = models.OneToOneField(
        "accounts.CustomUser", on_delete=models.CASCADE, related_name="teacher_profile"
    )
    department = models.CharField(max_length=100, null=True)
    subjects = models.ManyToManyField("hw.Subject", related_name="teachers")

    def __str__(self):
        return f"{self.user.username} (teacher)"
