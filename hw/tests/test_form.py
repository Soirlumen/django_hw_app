from .setUp import BaseHWTestCase
from django.test import override_settings, TestCase
from hw.models import Subject
from hw.forms import CreateHomeworkForm, MultipleFileField, AssignemntEdit, AssignmentForm,HomeworkForm
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.utils.datastructures import MultiValueDict
from django.http import QueryDict

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
          self.assertIn("Již zveřejněné zadání nelze upravovat.", str(form.errors)) 

          
class TestCreateHomeworkForm(BaseHWTestCase):
     def test_homework_form_valid_with_text(self):
        form_data = {"engrossment": "Odevzdaný úkol", "programming_language": "python", "notes": ""}
        form = CreateHomeworkForm(
            data=form_data,
            assignment=self.assignment,
            user=self.student,
        )
        self.assertTrue(form.is_valid(), form.errors)

     def test_homework_form_valid_with_file_only(self):
          uploaded_file = SimpleUploadedFile( "solution.py",b"print('hello')", content_type="text/x-python")
          files = MultiValueDict({"filesimput": [uploaded_file]})
          form_data = {
               "engrossment": "",
               "programming_language": "python",
               "notes": "",
          }
          form = CreateHomeworkForm(
               data=form_data,
               files=files,
               assignment=self.assignment,
               user=self.student,
          )
          self.assertTrue(form.is_valid(), form.errors)

     def test_homework_form_valid_with_text_and_file(self):
          uploaded_file = SimpleUploadedFile(
               "solution.py",
               b"print('hello')",
               content_type="text/x-python",
          )
          files = MultiValueDict({"filesimput": [uploaded_file]})
          form_data = {"engrossment": "Řešení je také napsané v editoru.", "programming_language": "python", "notes": ""}
          form = CreateHomeworkForm(
               data=form_data,
               files=files,
               assignment=self.assignment,
               user=self.student,
          )
          self.assertTrue(form.is_valid(), form.errors)

     def test_homework_form_invalid_without_text_or_file(self):
          form_data = {"engrossment": "", "programming_language": "python", "notes": ""}
          form = CreateHomeworkForm(
               data=form_data,
               assignment=self.assignment,
               user=self.student,
          )

          self.assertFalse(form.is_valid())
          self.assertIn("Vyplňte text řešení nebo přiložte alespoň jeden soubor.", str(form.non_field_errors()))

     def test_homework_form_invalid_with_whitespace_only(self):
          form_data = {"engrossment": "   \n\t", "programming_language": "python", "notes": ""}
          form = CreateHomeworkForm(
               data=form_data,
               assignment=self.assignment,
               user=self.student,
          )

          self.assertFalse(form.is_valid())
          self.assertIn("Vyplňte text řešení nebo přiložte alespoň jeden soubor.", str(form.non_field_errors()))

     def test_homework_form_invalid_programming_language(self):
          form_data = {"engrossment": "Odevzdaný úkol","programming_language": "ruby","notes": "proč tam nemám dobrou syntaxi?"}
          form = CreateHomeworkForm(
               data=form_data,
               assignment=self.assignment,
               user=self.student,
          )
          self.assertFalse(form.is_valid())
          self.assertIn(
               "Neplatný programovací jazyk.",
               str(form.errors),
          )

     def test_missing_student(self):
          form_data = {"engrossment": "Odevzdaný úkol", "programming_language": "python","notes": ""}
          form = CreateHomeworkForm(
               data=form_data,
               assignment=self.assignment,
          )
          self.assertFalse(form.is_valid())
          self.assertIn(
               "Chybí autor odevzdávaného řešení.",
               str(form.non_field_errors()),
          )

     def test_missing_assignment(self):
          form_data = {"engrossment": "Odevzdaný úkol", "programming_language": "python", "notes": ""}
          form = CreateHomeworkForm(
               data=form_data,
               user=self.student,
          )
          self.assertFalse(form.is_valid())
          self.assertIn(
               "Chybí zadání, ke kterému má být řešení odevzdáno.",
               str(form.non_field_errors()),
          )

     def test_cannot_submit_before_release(self):
          self.assignment.release = timezone.now() + timedelta(days=1)
          self.assignment.deadline = timezone.now() + timedelta(days=2)
          self.assignment.save(
               update_fields=["release", "deadline"]
          )

          form = CreateHomeworkForm(
               data={
                    "engrossment": "Řešení",
                    "programming_language": "python",
                    "notes": "",
               },
               assignment=self.assignment,
               user=self.student,
          )

          self.assertFalse(form.is_valid())
          self.assertIn(
               "Zadání ještě nebylo zveřejněno.",
               str(form.non_field_errors()),
          )

     def test_cannot_submit_after_deadline(self):
          self.assignment.release = timezone.now() - timedelta(days=2)
          self.assignment.deadline = timezone.now() - timedelta(days=1)
          self.assignment.save(
               update_fields=["release", "deadline"]
          )

          form = CreateHomeworkForm(
               data={
                    "engrossment": "Řešení",
                    "programming_language": "python",
                    "notes": "",
               },
               assignment=self.assignment,
               user=self.student,
          )

          self.assertFalse(form.is_valid())
          self.assertIn(
               "Úkol již nelze odevzdat, protože vypršel termín.",
               str(form.non_field_errors()),
          )

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
          
class TestHomeworkForm(BaseHWTestCase):
     def test_edit_valid_engrosm(self):
          data = QueryDict("", mutable=True)
          data.update({"engrossment": "upravila jsem řešení:)",
                    "programming_language": "python",
                    "notes": "",})
          form=HomeworkForm(
               data=data,
               instance=self.homework)
          self.assertTrue(form.is_valid(), form.errors)

     def test_edit_valid_no_engross_just_files(self):
          data = QueryDict("", mutable=True)
          data.update({"engrossment": "","programming_language": "python", "notes": ""})
          form = HomeworkForm(data=data, instance=self.homework)
          self.assertEqual(self.homework.total_files(), 1)
          self.assertTrue(form.is_valid(), form.errors)

     def test_edit_invalid_files_and_engs_removed(self):
          data = QueryDict("", mutable=True)
          data.update({"engrossment": "", "programming_language": "python","notes": ""})
          data.setlist( "remove_files", [str(self.codefile.pk)])
          form = HomeworkForm( data=data, instance=self.homework)
          self.assertFalse(form.is_valid())
          self.assertIn("Vyplňte text řešení nebo přiložte alespoň jeden soubor.",
               str(form.non_field_errors()))

     def test_edit_after_deadline_invalid(self):
          self.assignment.deadline = timezone.now() - timedelta(minutes=1)
          self.assignment.save(update_fields=["deadline"])

          form = HomeworkForm(
               data={"engrossment": "Upravené řešení", "programming_language": "python", "notes": "jhgfchkgc",},
               instance=self.homework)
          self.assertFalse(form.is_valid())
          self.assertIn(
               "Úkol již nelze upravit, protože vypršel termín.",
               str(form.non_field_errors()),
          )