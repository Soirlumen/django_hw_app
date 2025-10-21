from django.db import models
from django.urls import reverse
import datetime
from django.core.exceptions import ValidationError
from django.db.models import UniqueConstraint, CheckConstraint, Q, F
from django.conf import settings
from django.utils import timezone

YEAR_CHOICES = []
for r in range(1950, (datetime.datetime.now().year + 1)):
    YEAR_CHOICES.append((r, r))


class Subject(models.Model):
    year = models.IntegerField(
        choices=YEAR_CHOICES, default=datetime.datetime.now().year
    )
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.year}-{self.name}"


class Assignment(models.Model):
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, null=True, on_delete=models.SET_NULL)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField()
    max_score = models.PositiveSmallIntegerField(null=True)
    deadline = models.DateTimeField()
    release = models.DateTimeField()
    
    @property
    def after_deadline(self)->bool:
        return self.deadline>timezone.now()
    @property
    def before_release(self)->bool:
        return self.release<timezone.now()
    @property
    def active(self)->bool:
        return (not self.before_release and not self.after_deadline)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("hw_detail", kwargs={"pk": self.key.assignment.pk})

    class Meta:
        ordering = [
            "release",
        ]

class Key(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student}-{self.assignment}"
    def clean(self):
        subj = self.assignment.subject
        if not subj.subject_type.filter(user=self.student, role="student").exists():
            raise ValidationError("Uživatel není studentem tohoto předmětu.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        constraints = [
            UniqueConstraint(fields=["student", "assignment"], name="student_assgn")
        ]

class Homework(models.Model):
    ## část pro studenta
    key = models.OneToOneField(Key, on_delete=models.CASCADE, null=False)
    engrossment = models.TextField()  # solution ale hustští
    submitted = models.DateTimeField(null=(False == False))
    ## část pro učitele
    score = models.PositiveSmallIntegerField(null=True)
    text_evaluation = models.TextField(null=True)

    def __str__(self):
        return f"homework-{self.key}"

    def get_absolute_url(self):
        return reverse("hw_detail", kwargs={"pk": self.pk})
