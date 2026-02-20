from .setUp import BaseHWTestCase
from django.test import TestCase
from hw.models import Homework, Assignment, HomeworkStudentComment, Key, Subject
from accounts.models import CustomUser
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError

'''class AssignmentValidationTest(BaseHWTestCase):
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
'''
class TestSubject(TestCase):
    def setUp(self):
        self.subject=Subject(year=1980, name="INTA")
    def test_to_str(self):
        self.assertEqual(str(self.subject), "1980-INTA")
        
class TestAssignment(BaseHWTestCase):
    def test_to_str(self):
        self.assertEqual(str(self.assignment),"Domácí úkol 1")
    def test_property_if_comments_exists(self):
        self.assertEqual(self.assignment.is_comments_generated,True)   
        self.studentComment.delete()
        self.studentComment2.delete()
        self.assertEqual(self.assignment.is_comments_generated,False)   

class TestKey(BaseHWTestCase):
    def test_to_str(self):
        self.assertEqual(str(self.key),"student-Domácí úkol 1")   
    def test_validate_subject_exists(self):
        self.assignment.subject=None
        self.assertEqual(self.assignment.subject,None)
        with self.assertRaises(ValidationError):
            self.key.clean()
    def test_validate_student_has_not_subject(self):
        self.subject1 = Subject.objects.create(
               name="pgr12",
               year=2027
          )
        self.assgnmt=Assignment.objects.create(
               title="Domácí úkol k",
               subject=self.subject1,
               teacher=self.teacher,
               description="Testovací zadání",
               max_score=10,
               release=timezone.now() - timedelta(days=1),
               deadline=timezone.now() + timedelta(days=1),
          )
        self.key4=Key(
            student=self.student,
            assignment=self.assgnmt
        )
        with self.assertRaises(ValidationError):
            self.key4.clean()
    def test_unique_constraint_stud_assgn(self):
        self.key2=Key(student=self.student,assignment=self.assignment)
        