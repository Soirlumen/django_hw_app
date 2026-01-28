from .setUp import BaseHWTestCase
from hw.models import Homework, Assignment, ReviewHomework, Key
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError

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
            
    def test_deadline_equal_release_is_valid(self):
        now = timezone.now()
        ass = Assignment(
            title="OK úkol",
            subject=self.subject,
            teacher=self.teacher,
            description="...",
            max_score=10,
            release=now,
            deadline=now,
        )
        ass.full_clean()            

    def test_score_within_limit_is_valid(self):
        ev = Homework(
          key=self.key,
          engrossment = f"modelsbla",
          submitted = timezone.now(),
          text_evaluation= f"bla",
          score=6,
        )
        ev.full_clean() 

class HomeworkFlowTest(BaseHWTestCase):
    def test_student_can_submit_homework(self):
        hw = Homework.objects.create(
            key=self.key,
            score=8,
            submitted=timezone.now()
        )
        self.assertEqual(hw.score, 8)
        self.assertEqual(hw.key.student, self.student)
def test_unique_hw_reviewer(self):
    hw = Homework.objects.create(
        key=self.key,
        engrossment="x",
        submitted=timezone.now(),
        score=5,
    )

    ReviewHomework.objects.create(hw=hw, reviewer=self.teacher, comment="ok")

    with self.assertRaises(Exception):
        ReviewHomework.objects.create(hw=hw, reviewer=self.teacher, comment="dup")


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

class ModelStrTest(BaseHWTestCase):
    def test_assignment_str(self):
        self.assertEqual(str(self.assignment), "Domácí úkol 1")
        
class KeyConstraintTest(BaseHWTestCase):
     def test_student_cannot_have_two_keys_for_assignment(self):
          with self.assertRaises(Exception):
               Key.objects.create(
                    student=self.student,
                    assignment=self.assignment
               )
