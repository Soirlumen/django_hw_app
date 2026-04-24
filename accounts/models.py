from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    first_name=models.CharField(max_length=50,null=True, blank=True,verbose_name=_("Jméno"),help_text=_("Křestní jméno uživatele."),)
    surname=models.CharField(max_length=50,null=True, blank=True,verbose_name=_("Příjmení"),help_text=_("Příjmení uživatele."),)
    tel = PhoneNumberField(blank=True, region="CZ",verbose_name=_("Telefon"), help_text=_("Telefonní číslo ve správném formátu."),)
    subjects=models.ManyToManyField("hw.Subject",through="accounts.SubjectType",
                                    through_fields=("user","subject") ,
                                    related_name="users", verbose_name=_("Předměty"),
                                    help_text=_("Předměty, ke kterým je uživatel přiřazen."),)
    def __str__(self):
        full_name = f"{self.first_name or ''} {self.surname or ''}".strip()
        return full_name or self.username

    @property
    def is_teacher(self)->bool:
        return self.subject_type.filter(role="teacher").exists()
    @property
    def is_student(self)->bool:
        return self.subject_type.filter(role="student").exists()
    @property
    def teacher_subjects(self):
        return self.subjects.filter(subject_type__role="teacher")
    @property
    def student_subjects(self):
        return self.subjects.filter(subject_type__role="student")
    class Meta:
        verbose_name = _("Uživatel")
        verbose_name_plural = _("Uživatelé")

class SubjectType(models.Model):
    ROLE_CHOICES = [
        ("student", _("Student")),
        ("teacher", _("Vyučující")),
        ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="subject_type",verbose_name=_("Uživatel"),)
    subject = models.ForeignKey(
        "hw.Subject", on_delete=models.CASCADE, related_name="subject_type",verbose_name=_("Předmět"))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES,verbose_name=_("Role"),help_text=_("Role uživatele v daném předmětu."),)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "subject"], name="unique_user_subject"
            ),
            models.CheckConstraint(
                condition=models.Q(role__in=["student", "teacher"]),
                name="role_valid",
            ),
        ]
        verbose_name = _("Přiřazení role k předmětu")
        verbose_name_plural = _("Přiřazení rolí k předmětům")

    def __str__(self):
        return f"{self.user.username} - {self.subject} ({self.role})"