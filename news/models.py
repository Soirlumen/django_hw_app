from django.db import models
from django.utils.translation import gettext_lazy as _

class NewsPost(models.Model):
     date=models.DateTimeField()
     announcement=models.TextField()
     class Meta:
          verbose_name = _("Novinka")
          verbose_name_plural = _("Novinky")
     