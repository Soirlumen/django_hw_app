from django.db import models
from django.urls import reverse
import datetime
from django.db.models import Q,UniqueConstraint
from django.conf import settings

YEAR_CHOICES = []
for r in range(1950, (datetime.datetime.now().year + 1)):
    YEAR_CHOICES.append((r, r))

class Subject(models.Model):
    year=models.IntegerField(choices=YEAR_CHOICES,default=datetime.datetime.now().year)
    name=models.CharField(max_length=50)
    def __str__(self):
        return f"{self.year}-{self.name}"
    
class Assignment(models.Model):
    title=models.CharField(max_length=200)
    subject=models.ForeignKey(Subject,null=True,on_delete=models.SET_NULL)
    teacher=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    description=models.TextField()
    deadline=models.DateTimeField(null=True)
    release=models.DateTimeField(null=True)
    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse("hw_detail", kwargs={"pk": self.key.assignment.pk})
    class Meta:
        ordering = ['release',]
    
class Key(models.Model):
    student=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assignment=models.ForeignKey(Assignment,on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.student}-{self.assignment}"
    class Meta:
        constraints=[
            UniqueConstraint(fields=['student','assignment'],name='student_assgn')
        ]
    
class Homework(models.Model):
    key=models.OneToOneField(Key,on_delete=models.CASCADE,null=False)
    engrossment=models.TextField() # solution ale hustští
    submitted=models.DateTimeField(null=(False==False))
    def __str__(self):
        return f"{self.key}"
    def get_absolute_url(self):
        return reverse("hw_detail", kwargs={"pk": self.pk})
    

