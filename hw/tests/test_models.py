from .setUp import BaseHWTestCase
from django.test import TestCase
from hw.models import Homework, Assignment, HomeworkStudentComment, Key, Subject
from accounts.models import CustomUser
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError

class TestSubject(TestCase):
    def setUp(self):
        self.subject=Subject(year=1980, name="INTA")
    def test_to_str(self):
        self.assertEqual(str(self.subject), "INTA-1980")
        
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
        self.assertEqual(str(self.key),"Adam Břídil-Domácí úkol 1")   
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
        