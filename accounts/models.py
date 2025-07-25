from django.contrib.auth.models import AbstractUser
from django.db import models
class CustomUser(AbstractUser):
    grade = models.PositiveIntegerField(null=True, blank=True)
    
