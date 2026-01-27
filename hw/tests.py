from django.test import TestCase
from .models import *
import datetime
from accounts.models import *

from django.core.exceptions import ValidationError
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


class AssignmentValidationTest(BaseHWTestCase):
    def test_deadline_before_release_is_invalid(self):
        ass = Assignment(
            title="Chybný úkol",
            subject=self.subject,
            teacher=self.teacher,
            description="...",
            max_score=5,
            release=timezone.now(),
            deadline=timezone.now() - timedelta(days=1),
        )

        with self.assertRaises(ValidationError):
            ass.full_clean()

class ScoreEvaluationTest(BaseHWTestCase):
     def test_score_maxscore(self):
          ev=Homework(
          key=self.key,
          engrossment = f"modelsbla",
          submitted = timezone.now(),
          text_evaluation= f"bla",
          score=60,
          )
          with self.assertRaises(ValidationError):
               ev.full_clean()
          