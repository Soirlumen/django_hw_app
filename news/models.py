from django.db import models

class NewsPost(models.Model):
     date=models.DateTimeField()
     announcement=models.TextField()