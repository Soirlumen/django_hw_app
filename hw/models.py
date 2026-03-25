from django.db import models
from django.urls import reverse
import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import UniqueConstraint
from django.conf import settings
import os
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

YEAR_CHOICES = []
for r in range(1950, (datetime.datetime.now().year + 1)):
    YEAR_CHOICES.append((r, r))
LANGUAGE_CHOICES = (
    ("python", "Python"),
    ("text/x-c++src", "C++"),
    ("text/x-java", "Java"),
    ("markdown", "Markdown"),
    ("null", _("Prostý text")),
)
def validate_file_size(value):
    if value.size > settings.MAX_UPLOAD_FILE_SIZE:
        raise ValidationError(
    _("Maximální velikost jednoho souboru je %(maxsize)s MB.")% {"maxsize": f"{settings.MAX_UPLOAD_FILE_SIZE_MB:.0f}"})


def codefile_upload(instance, filename):
    user = getattr(instance, "_upload_user", None)
    assignment = getattr(instance, "_upload_assignment", None)

    username = slugify(user.username) if user else "unknown-user"
    assignment_name = slugify(assignment.title) if assignment else "unknown-assignment"

    return os.path.join(username, assignment_name, filename)

class Subject(models.Model):
    year = models.IntegerField(
        choices=YEAR_CHOICES, default=datetime.datetime.now().year,verbose_name=_("Rok"),help_text=_("Rok vyučovaného předmětu."),)
    name = models.CharField(max_length=50,verbose_name=_("Název předmětu"),help_text=_("Zadejte zkratku předmětu."),)
    class Meta:
        verbose_name = _("Předmět")
        verbose_name_plural = _("Předměty")
    def __str__(self):
        return str(self.name).upper()+"-"+ str(self.year)

class CodeFile(models.Model):
    file = models.FileField(
        upload_to=codefile_upload,
        validators=[validate_file_size],
        verbose_name=_("Soubor"),)
    class Meta:
        verbose_name = _("Soubor")
        verbose_name_plural = _("Soubory")
    @property
    def get_file_path(self)->str:
        return self.file.url
    def __str__(self):
        return os.path.basename(self.file.name)
    def delete(self, *args, **kwargs):
        if self.file:
            self.file.delete(save=False)
        super().delete(*args, **kwargs)
    
class Assignment(models.Model):
    title = models.CharField(max_length=200, verbose_name=_("Titulek zadání"),help_text=_("Stručný titulek zadání k domácího úkolu."),)
    subject = models.ForeignKey(Subject, null=True, on_delete=models.SET_NULL,verbose_name=_("Předmět"),help_text=_("Vyberte předmět, ke kterému úkol patří."),)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Vyučující"),)
    description = models.TextField(max_length=30000,verbose_name=_("Popis"),help_text=_("Popište zadání domácího úkolu."),)
    files=models.ManyToManyField(CodeFile,blank=True, verbose_name=_("Přílohy"),)
    max_score = models.PositiveSmallIntegerField(null=True, verbose_name=_("Maximální počet bodů"),help_text=_("Maximálni počet bodů, který lze za úkol získat."),)
    release = models.DateTimeField(verbose_name=_("Zveřejnění"),help_text=_("Od tohoto času bude zadání dostupné."),)
    deadline = models.DateTimeField(verbose_name=_("Termín odevzdání"),help_text=_("Po tomto termínu již nelze úkol odevzdat."),
    )
    
    def __str__(self):
        return self.title
    def clean(self):
        if self.deadline < self.release:
            raise ValidationError({
                'deadline': _("Termín odevzdání nemůže být dříve než zveřejnění.")
            })
    @property
    def is_after_deadline(self)->bool:
        return timezone.now()>self.deadline
    @property
    def is_before_release(self)->bool:
        return timezone.now()<self.release
    @property
    def is_comments_generated(self)->bool:
        return HomeworkStudentComment.objects.filter(hw__key__assignment=self).exists()
    def total_files(self)->int:
        return self.files.count()
    class Meta:
        ordering = [
            "release",
        ]
        verbose_name = _("Zadání")
        verbose_name_plural = _("Zadání")
        
    def get_url(self):
        return reverse("assgn_detail_teacher", kwargs={"pk":self.pk})

class Key(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Student"))
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='homework_assignment',verbose_name=_("Zadání"))

    def __str__(self):
        return f"{self.student}-{self.assignment}"
    def clean(self):
        subj = self.assignment.subject
        if subj is None:
            raise ValidationError(_("Úkol nemá přiřazený předmět."))

        if not subj.subject_type.filter(user=self.student, role="student").exists():
            raise ValidationError(_("Uživatel není studentem tohoto předmětu."))

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        constraints = [
            UniqueConstraint(fields=["student", "assignment"], name="student_assgn")
        ]
        verbose_name = _("Přiřazení úkolu")
        verbose_name_plural = _("Přiřazení úkolů")

class Homework(models.Model):
    ## část pro studenta
    key = models.OneToOneField(Key, on_delete=models.CASCADE, null=False,verbose_name=_("Klíč úkol-student"))
    programming_language = models.CharField(max_length=32,choices=LANGUAGE_CHOICES, default="python", 
                                            verbose_name=_("Programovací jazyk"), help_text=_("Vyberte programovací jazyk, ve kterém napíšete řešení úkolu."),)
    engrossment = models.TextField(verbose_name=_("Řešení"),help_text=_("Napište své řešení úkolu."),)  # solution ale hustští
    #files=models.ManyToManyField(CodeFile,blank=True, null=True)
    files=models.ManyToManyField(CodeFile,blank=True, verbose_name=_("Přiložené soubory"),)
    submitted = models.DateTimeField(null=True, blank=True,verbose_name=_("Odevzdáno"),)
    ## část pro učitele
    score = models.PositiveSmallIntegerField(null=True, blank=True,verbose_name=_("Počet bodů"), help_text=_("Počet bodů přidělený vyučujícím."),)
    text_evaluation = models.TextField(null=True, blank=True,verbose_name=_("Slovní hodnocení"))
    def __str__(self):
        return f"homework-{self.key}"
    def total_files(self)->int:
        return self.files.count()
    def get_assgn_student_url(self):
        return reverse("assgn_detail_student", kwargs={"pk":self.key.assignment.pk})
    @property
    def is_after_deadline(self)->bool:
        return timezone.now()>self.key.assignment.deadline
    class Meta:
        verbose_name = _("Odevzdaný úkol")
        verbose_name_plural = _("Odevzdané úkoly")

class HomeworkStudentComment(models.Model):
    hw = models.ForeignKey(Homework, on_delete=models.CASCADE,verbose_name=_("Úkol"),)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,verbose_name=_("Hodnotitel"),)
    comment = models.TextField(blank=True, default="",max_length=30000,verbose_name=_("Komentář"),help_text=_("Napište zpětnou vazbu k úkolu."))
    submitter=models.DateTimeField(null=True, blank=True,verbose_name=_("Odesláno"))

    def clean(self):
        if self.hw.key.student_id == self.reviewer_id:
            raise ValidationError(_("Hodnotitel nemůže být autor domácího úkolu."))
        if self.hw.key.assignment.teacher_id==self.reviewer_id:
            raise ValidationError(_("Hodnotitel  nemůže být autor zadání úkolu."))

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
        verbose_name = _("Studentský komentář")
        verbose_name_plural = _("Studentské komentáře")