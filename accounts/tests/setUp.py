from django.test import TestCase
from hw.models import *
from accounts.models import *
from django.utils import timezone
from datetime import timedelta

class BaseHWTestCase(TestCase):
     def setUp(self):
          # users
          self.teacher = CustomUser.objects.create_user(
               username="teacher",
               password="pass"
          )
          self.student = CustomUser.objects.create_user(
               username="student",
               password="pass"
          )

          # subject
          self.subject = Subject.objects.create(
               name="pgr2",
               year=2025
          )

          # vazby user - subject
          SubjectType.objects.create(
               user=self.teacher,
               subject=self.subject,
               role="teacher"
          )
          SubjectType.objects.create(
               user=self.student,
               subject=self.subject,
               role="student"
          )

          now = timezone.now()

          # assignment
          self.assignment = Assignment.objects.create(
               title="Domácí úkol 1",
               subject=self.subject,
               teacher=self.teacher,
               description="Testovací úkol",
               max_score=10,
               release=now - timedelta(days=1),
               deadline=now + timedelta(days=1),
          )
          # key
          self.key = Key.objects.create(
               student=self.student,
               assignment=self.assignment
          )
