from django.db import models
from django.urls import reverse
import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import UniqueConstraint
from django.conf import settings
import os


YEAR_CHOICES = []
for r in range(1950, (datetime.datetime.now().year + 1)):
    YEAR_CHOICES.append((r, r))


class Subject(models.Model):
    year = models.IntegerField(
        choices=YEAR_CHOICES, default=datetime.datetime.now().year
    )
    name = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name).upper()+"-"+ str(self.year)

class CodeFile(models.Model):
    file=models.FileField(upload_to="uploads/")
    @property
    def get_file_path(self)->str:
        return self.file.url
    def __str__(self):
        return os.path.basename(self.file.name)
    # def delete(self, *args, **kwargs):
    #     if self.file:
    #         self.file.delete(save=False) 
    #     super().delete(*args, **kwargs)
    
class TextFile(models.Model):
    LANGUAGE_CHOICES = (
    ("PYTHON", "python"),
    ("CPP", "cpp"),
    ("JAVA", "java"),
    ("DECEMBER", "December"),
)
    language=models.CharField(choices=LANGUAGE_CHOICES, default="PYTHON")
    text=models.TextField()
    
class Assignment(models.Model):
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, null=True, on_delete=models.SET_NULL)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField()
    files=models.ManyToManyField(CodeFile,blank=True)
    max_score = models.PositiveSmallIntegerField(null=True)
    deadline = models.DateTimeField()
    release = models.DateTimeField()

    def __str__(self):
        return self.title
    def clean(self):
        if self.deadline < self.release:
            raise ValidationError({
                'deadline': "Deadline nemůže být dříve než release."
            })
    @property
    def is_after_deadline(self)->bool:
        return timezone.now()>self.deadline
    @property
    def is_comments_generated(self)->bool:
        return HomeworkStudentComment.objects.filter(hw__key__assignment=self).exists()
    
    class Meta:
        ordering = [
            "release",
        ]

class Key(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='homework_assignment')

    def __str__(self):
        return f"{self.student}-{self.assignment}"
    def clean(self):
        subj = self.assignment.subject
        if subj is None:
            raise ValidationError("Úkol nemá přiřazený předmět.")

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
    #files=models.ManyToManyField(CodeFile,blank=True, null=True)
    files=models.ManyToManyField(CodeFile,blank=True)
    submitted = models.DateTimeField(null=True, blank=True)
    ## část pro učitele
    score = models.PositiveSmallIntegerField(null=True, blank=True)
    text_evaluation = models.TextField(null=True, blank=True)
    def __str__(self):
        return f"homework-{self.key}"

    def get_assgn_student_url(self):
        return reverse("assgn_detail_student", kwargs={"pk":self.key.assignment.pk})
    @property
    def is_after_deadline(self)->bool:
        return timezone.now()>self.key.assignment.deadline


class HomeworkStudentComment(models.Model):
    hw = models.ForeignKey(Homework, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField(blank=True, default="")
    submitter=models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.hw.key.student_id == self.reviewer_id:
            raise ValidationError("Reviewer nemůže být autor domácího úkolu.")
        if self.hw.key.assignment.teacher_id==self.reviewer_id:
            raise ValidationError("Reviewer nemůže být autor zadání úkolu.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["hw", "reviewer"],
                name="unique_hw_reviewer"
            )
        ]