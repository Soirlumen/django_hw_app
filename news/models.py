from django.db import models
from django.utils.translation import gettext_lazy as _

class NewsPost(models.Model):
     date=models.DateTimeField()
     announcement=models.TextField()
     class Meta:
          verbose_name = _("Přiřazení role k předmětu")
          verbose_name_plural = _("Přiřazení rolí k předmětům")
     