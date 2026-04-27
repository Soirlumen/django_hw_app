from .setUp import BaseHWTestCase
from django.test import TestCase, override_settings
from hw.models import Assignment, Key, Subject, CodeFile, HomeworkStudentComment
from django.utils import timezone
from datetime import timedelta
import os
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

class TestSubject(TestCase):
    def setUp(self):
        self.subject=Subject(year=1980, name="INTA")
    def test_to_str(self):
        self.assertEqual(str(self.subject), "INTA-1980")

@override_settings(DEFAULT_FILE_STORAGE='django.core.files.storage.InMemoryStorage')        
class TestAssignment(BaseHWTestCase):
    def test_to_str(self):
        self.assertEqual(str(self.assignment),"Domácí úkol 1")
    def test_property_is_comments_generated(self):
        self.assertEqual(self.assignment.is_comments_generated,True)   
        self.studentComment.delete()
        self.studentComment2.delete()
        self.assertEqual(self.assignment.is_comments_generated,False)   
    def test_clean_deadline_before_release(self):
        self.assgnmt=Assignment(
            title="Domácí úkol k",
            subject=self.subject,
            teacher=self.teacher,
            description="Testovací zadání",
            max_score=10,
            release=timezone.now() + timedelta(days=1),
            deadline=timezone.now() - timedelta(days=1),)
        with self.assertRaises(ValidationError):
            self.assgnmt.full_clean()
    def test_property_is_after_deadline(self):
        self.assertEqual(self.assignment.is_after_deadline, False)
        self.assignment.deadline=timezone.now() - timedelta(days=1)
        self.assignment.save()
        self.assertEqual(self.assignment.is_after_deadline, True)
    def test_proprty_is_before_release(self):
        self.assertEqual(self.assignment.is_before_release,False)
        self.assignment.release=timezone.now() + timedelta(days=1)
        self.andrasgnt=Assignment.objects.create(
            title="Domácí úkol k",
            subject=self.subject,
            teacher=self.teacher,
            description="Testovací zadání",
            max_score=10,
            release=timezone.now() + timedelta(days=1),
            deadline=timezone.now() + timedelta(days=2),)
        self.assertEqual(self.andrasgnt.is_before_release,True) 
    def test_total_files(self):
        self.assertEqual(self.assignment.total_files(),1)
        self.assignment.files.remove(self.codefile)
        self.assertEqual(self.assignment.total_files(),0)
    def test_get_url(self):
        url='/cs/hw/assignmentt/1/'
        self.assertIsInstance(self.assignment.get_url(),str)
        self.assertIn(self.assignment.get_url(),url)

@override_settings(DEFAULT_FILE_STORAGE='django.core.files.storage.InMemoryStorage')

class TestCodeFile(BaseHWTestCase):
    def test_to_str(self):
        self.assertIn("test_code",str(self.codefile))
    def test_validate_file_size(self):
        big_file = SimpleUploadedFile("big_file.py", b"x" * (settings.MAX_UPLOAD_FILE_SIZE + 1))
        codefile = CodeFile(file=big_file)
        with self.assertRaises(ValidationError):
            codefile.full_clean()
    def test_get_file_path_property(self):
        actual_path = self.codefile.get_file_path
        self.assertIsInstance(actual_path, str)
        self.assertIn("test_code", actual_path)
    def test_delete_file(self):
        file_path=self.codefile.file.path
        self.codefile.delete()
        self.assertFalse(os.path.exists(file_path))
    def test_total_files_multiple(self):
        another_file = SimpleUploadedFile("second.py", b"print('hello')")
        cf2 = CodeFile.objects.create(file=another_file)
        self.assignment.files.add(cf2)
        self.assertEqual(self.assignment.total_files(), 2)
        self.assignment.files.remove(cf2)
        self.assertEqual(self.assignment.total_files(), 1)
    
class TestKey(BaseHWTestCase):
    def test_to_str(self):
        str_key=f"{self.student.first_name} {self.student.surname}-{self.assignment.title}"
        self.assertEqual(str(self.key), str_key)   
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
        
class TestHomework(BaseHWTestCase):
    def test_to_str(self):
        str_hw="homework-Daniela Hušhuš-Domácí úkol 1"
        self.assertEqual(str(self.homework), str_hw)
    def test_total_files(self):
        self.assertEqual(self.homework.total_files(), 1)
    def test_get_aasgn_student_url(self):
        url='/cs/hw/assignments/1/'
        self.assertIsInstance(url, str)
        self.assertIn("hw", url)
        self.assertIn(str(self.assignment.pk), url)
        self.assertIn("assignments", url) # najde to stránku zadání pro studenty
    def test_is_after_deadline(self):
        self.assertEqual(self.assignment.is_after_deadline, False)
        self.assignment.deadline=timezone.now() - timedelta(days=1)
        self.assignment.save()
        self.assertEqual(self.assignment.is_after_deadline, True)
    
class TestHomeworkStudentComment(BaseHWTestCase):
    def test_to_str(self):
        str_comment="Comment: Vojta Lustr of hw homework-Daniela Hušhuš-Domácí úkol 1"
        self.assertEqual(str(self.studentComment), str_comment)
    def test_comment_constraints(self):
        comment=HomeworkStudentComment(hw=self.homework, reviewer=self.student, comment="test")
        with self.assertRaises(ValidationError):
            comment.full_clean()
    def test_save_and_clean(self):
        comment = HomeworkStudentComment(hw=self.homework3,
                                         reviewer=self.student2,
                                        comment="cool")
        comment.save()
        self.assertIsNotNone(comment.submitter)
        self.assertLess((timezone.now() - comment.submitter).total_seconds(), 5)# plus par sekund nevim jak je rychlý testik
        
    def test_cannot_review_own_assgn(self):
        comment = HomeworkStudentComment(hw=self.homework, reviewer=self.assignment.teacher, comment="nejlepší co jsem kdy viděl")
        with self.assertRaises(ValidationError):
            comment.full_clean()
    def test_cannot_review_teacher(self):
        comment = HomeworkStudentComment(hw=self.homework, reviewer=self.assignment.teacher, comment="paráda")
        with self.assertRaises(ValidationError):
            comment.full_clean()