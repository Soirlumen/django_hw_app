from .setUp import BaseHWTestCase
from django.test import override_settings, TestCase
from hw.models import HomeworkStudentComment, Assignment, Homework, Subject
from hw.forms import CreateHomeworkForm, MultipleFileField, MultipleFileInput,HomeworkForm, AssignemntEdit, AssignmentForm, EvaluationForm, HomeworkStudentCommentForm
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

@override_settings(DEFAULT_FILE_STORAGE='django.core.files.storage.InMemoryStorage')
class TestAssignmentForm(BaseHWTestCase):
     def test_valid_form(self):
          form_data = {
               "title": "Domácí úkol 2",
               "subject": self.subject.pk,
               "description": "Další testovací zadání",
               "release": (timezone.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M"),
               "deadline": (timezone.now() + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M"),
               "max_score": 10
          }
          form = AssignmentForm(data=form_data, user=self.teacher)
          self.assertTrue(form.is_valid())
          
     def test_cannot_see_or_take_not_owned_subject(self):
          hehe_subj=Subject.objects.create(name="hehe", year=2026)
          data={
               "title": "hehe",
               "subject": hehe_subj.pk,
               "description": "...",
               "release": (timezone.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M"),
               "deadline": (timezone.now() + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M"),
               "max_score": 10
          }
          asform=AssignmentForm(data=data, user=self.teacher)
          self.assertFalse(asform.is_valid())
          self.assertIn("Na tomto předmětu nejsi veden jako učitel.", str(asform.errors))
     def test_student_cannot_create_assignment(self):
          hehe_subj=Subject.objects.create(name="hehe", year=2026)
          data={
               "title": "hehe",
               "subject": hehe_subj.pk,
               "description": "...",
               "release": (timezone.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M"),
               "deadline": (timezone.now() + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M"),
               "max_score": 10
          }
          asform=AssignmentForm(data=data, user=self.student)
          self.assertFalse(asform.is_valid())
          self.assertIn("Na tomto předmětu nejsi veden jako učitel.", str(asform.errors))
          
     def test_assignment_form_deadline_before_release(self):
          form_data = {
               "title": "Špatný úkol",
               "subject": self.subject.pk,
               "description": "...",
               "release": (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M"),
               "deadline": (timezone.now() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M"),
               "max_score": 10
          }
          form = AssignmentForm(data=form_data, user=self.teacher)
          self.assertFalse(form.is_valid())
          self.assertIn("Termín odevzdání nemůže být dříve než zveřejnění", str(form.errors))
     def test_no_user(self): #další chybka
          self.assignment.release = timezone.now() + timedelta(minutes=10)
          form_data={
               "title": self.assignment.title,
               "subject": self.assignment.subject.pk,
               "description": self.assignment.description,
               "release": (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M"),
               "deadline": (timezone.now() + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M"),
               "max_score": self.assignment.max_score
          }
          form=AssignmentForm(data=form_data, instance=self.assignment)
          self.assertFalse(form.is_valid())   
          self.assertIn("Chybí autor zadání.", str(form.errors)) 

class TestAssignemntEdit(BaseHWTestCase):
     def test_assignment_edit_deadline_before_release(self):
          self.assignment.release = timezone.now() + timedelta(minutes=10)
          form_data = {
               "title": self.assignment.title,
               "subject": self.assignment.subject.pk,
               "description": self.assignment.description,
               "release": (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M"),
               "deadline": (timezone.now() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M"),
               "max_score": self.assignment.max_score
          }
          form = AssignemntEdit(data=form_data, instance=self.assignment)
          self.assertFalse(form.is_valid())
          self.assertIn("Termín odevzdání nemůže být dříve než zveřejnění", str(form.errors))
     def test_assignment_edit_valid(self):
          self.assignment.release = timezone.now() + timedelta(minutes=10)
          form_data = {
               "title": self.assignment.title,
               "subject": self.assignment.subject.pk,
               "description": self.assignment.description,
               "release": (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M"),
               "deadline": (timezone.now() + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M"),
               "max_score": self.assignment.max_score
          }
          form = AssignemntEdit(data=form_data, instance=self.assignment)
          self.assertTrue(form.is_valid())
     def test_assignment_edit_after_release(self):
          self.assignment.release = timezone.now() - timedelta(days=1)
          form_data = {
               "title": self.assignment.title,
               "subject": self.assignment.subject.pk,
               "description": self.assignment.description,
               "release": (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M"),
               "deadline": (timezone.now() + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M"),
               "max_score": self.assignment.max_score
          }
          form=AssignemntEdit(data=form_data, instance=self.assignment)
          self.assertFalse(form.is_valid())
          self.assertIn("Nelze editovat zadání, jestliže je již aktivní.", str(form.errors)) 

          
class TestCreateHomeworkForm(BaseHWTestCase):
     def test_homework_form_valid(self):
          form_data={
               "engrossment":"Odevzdaný úkol",
               "programming_language":"python",
          }
          form=CreateHomeworkForm(data=form_data, assignment=self.assignment)
          self.assertTrue(form.is_valid())
     def test_homework_form_invalid_programming_language(self):
          form_data={
               "engrossment":"Odevzdaný úkol",
               "programming_language":"ruby",
          }
          form=CreateHomeworkForm(data=form_data, assignment=self.assignment)
          self.assertFalse(form.is_valid())
          self.assertIn("Neplatný programovací jazyk.", str(form.errors))
          
          
     def test_no_user(self): # další chybka
          form_data={
               "engrossment":"Odevzdaný úkol",
               "programming_language":"python",
          }
          form=CreateHomeworkForm(data=form_data, assignment=self.assignment)
          self.assertFalse(form.is_valid())
          self.assertIn("Chybí autor úkolu.", str(form.errors))

@override_settings(DEFAULT_FILE_STORAGE='django.core.files.storage.InMemoryStorage')
class TestMultipleFileField(TestCase):
     def setUp(self):
          self.field = MultipleFileField(required=False)
         
     def test_clean_correct(self):
          file1=SimpleUploadedFile("file1.txt", b"fnj")
          file2=SimpleUploadedFile("file2.txt", b"bnj")
          cleane_data=self.field.clean([file1,file2])
          self.assertEqual(cleane_data,[file1,file2])
          self.assertEqual(len(cleane_data),2)
     @override_settings(MAX_UPLOAD_FILES_NUMBER=2)
     def test_clean_too_much_files(self):
          file1=SimpleUploadedFile("file1.txt", b"fnj")
          file2=SimpleUploadedFile("file2.txt", b"bnj")
          file3=SimpleUploadedFile("file3.txt", b"knj")
          with self.assertRaises(ValidationError) as ve:
               self.field.clean([file1,file2,file3])
          self.assertIn("Najednou můžeš nahrát maximálně 2 souborů.", str(ve.exception))
     @override_settings(MAX_UPLOAD_FILE_SIZE=10)
     def test_too_big_file(self):
          too_much_a = b"a" * (11)
          big_file = SimpleUploadedFile("big_file.txt", too_much_a)
          with self.assertRaises(ValidationError) as ve:
               self.field.clean([big_file])
          self.assertIn("Soubor big_file.txt je příliš velký. Maximum je 0 MB.", str(ve.exception)) #protože 10 bajtů je méně než 1 MB, tak se to zaokrouhluje na 0...
     def test_clean_no_files(self):
          cleaned_data=self.field.clean(None)
          cleaned_data1=self.field.clean([])
          self.assertEqual(cleaned_data,[])
          self.assertEqual(cleaned_data1,[])
          