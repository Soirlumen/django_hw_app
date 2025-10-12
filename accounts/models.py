from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class CustomUser(AbstractUser):
    first_name=models.CharField(max_length=50,null=True, blank=True)
    surname=models.CharField(max_length=50,null=True, blank=True)
    tel = PhoneNumberField(blank=True, region="CZ")
    subjects=models.ManyToManyField("hw.Subject",through="accounts.SubjectType",through_fields=("user","subject") ,related_name="users",)
    @property
    def is_teacher(self)->bool:
        return self.subject_type.filter(role="teacher").exists()
    @property
    def is_student(self)->bool:
        return self.subject_type.filter(role="student").exists()
    
    def __str__(self):
        return self.username
    
    @property
    def teacher_subjects(self):
        return self.subjects.filter(subject_type__role="teacher")

    @property
    def student_subjects(self):
        return self.subjects.filter(subject_type__role="student")

class SubjectType(models.Model):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("teacher", "Teacher"),
    ]

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="subject_type"
    )
    subject = models.ForeignKey(
        "hw.Subject", on_delete=models.CASCADE, related_name="subject_type"
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "subject"], name="unique_user_subject"
            ),
            models.CheckConstraint(
                check=models.Q(role__in=["student", "teacher"]),
                name="role_valid",
            ),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.subject} ({self.role})"
