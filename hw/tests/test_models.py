from .setUp import BaseHWTestCase
from django.test import TestCase, override_settings
from hw.models import Assignment, Key, Subject, CodeFile, HomeworkStudentComment
from django.utils import timezone
from datetime import timedelta
import os
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from hw.shuffle import get_the_houmwrk

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
    def test_property_is_before_release(self):
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
        self.assertIsInstance(self.assignment.get_url(), str)
        expected_url = f'/cs/hw/assignmentt/{self.assignment.pk}/'
        self.assertEqual(self.assignment.get_url(), expected_url)
    def test_clean_validate_max_file_count(self):
        pass

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
    def test_get_assgn_student_url(self):
        expected_url = f'/cs/hw/assignments/{self.assignment.pk}/'
        self.assertIsInstance(expected_url, str)
        self.assertEqual(self.homework.get_assgn_student_url(), expected_url)
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
        self.assertIsNotNone(comment.submitted)
        self.assertLess((timezone.now() - comment.submitted).total_seconds(), 5)# plus par sekund nevim jak je rychlý testik
        
    def test_cannot_review_own_assgn(self):
        comment = HomeworkStudentComment(hw=self.homework, reviewer=self.assignment.teacher, comment="nejlepší co jsem kdy viděl")
        with self.assertRaises(ValidationError):
            comment.full_clean()
            
    def test_cannot_review_teacher(self):
        comment = HomeworkStudentComment(hw=self.homework, reviewer=self.assignment.teacher, comment="paráda")
        with self.assertRaises(ValidationError):
            comment.full_clean()
            

class GetTheHoumwrkTests(TestCase):

    def test_empty_or_single_homework_returns_empty_list(self):
        """Pokud je odevzdaných úkolů méně než 2, má funkce vrátit prázdný seznam."""
        self.assertEqual(get_the_houmwrk([], k=1), [])
        self.assertEqual(get_the_houmwrk(["hw1"], k=1), [])

    def test_k_less_than_one_returns_empty_list(self):
        """Pokud je k menší než 1, funkce nic nepřiřadí a vrátí prázdný seznam."""
        self.assertEqual(get_the_houmwrk(["hw1", "hw2", "hw3"], k=0), [])
        self.assertEqual(get_the_houmwrk(["hw1", "hw2", "hw3"], k=-1), [])

    def test_k_greater_than_max_raises_value_error(self):
        """Pokud je k větší než n-1, musí funkce vyhodit ValueError."""
        with self.assertRaises(ValueError):
            get_the_houmwrk(["hw1", "hw2", "hw3"], k=3)  # n=3, max k je 2

    def test_reviewer_never_reviews_themselves(self):
        """Ověření, že v žádné dvojici nefiguruje stejný úkol jako hodnotitel i hodnocený."""
        homeworks = [f"hw_{i}" for i in range(5)]
        pairs = get_the_houmwrk(homeworks, k=2)
        
        self.assertEqual(len(pairs), 5)
        for reviewer, to_review in pairs:
            # Nikdo nesmí hodnotit sám sebe
            self.assertNotIn(reviewer, to_review)
            # Každý musí dostat přesně k úkolů
            self.assertEqual(len(to_review), 2)

    def test_deterministic_shuffling_with_seed(self):
        """Pokud zadáme stejný seed, výstup musí být vždy identický."""
        homeworks = ["A", "B", "C", "D", "E"]
        
        res1 = get_the_houmwrk(homeworks, k=2, seed=42)
        res2 = get_the_houmwrk(homeworks, k=2, seed=42)
        res3 = get_the_houmwrk(homeworks, k=2, seed=7)
        
        self.assertEqual(res1, res2)
        self.assertNotEqual(res1, res3)  # Jiný seed by měl udělat jiný mix

    def test_cyclical_assignment_correctness(self):
        """Ověření, že algoritmus správně posouvá indexy cyklicky dokola."""
        homeworks = ["A", "B", "C"]
        # Použijeme seed, u kterého víme, jak dopadne shuffle, nebo otestujeme 
        # pouze vlastnost cykličnosti: prvek na indexu i + 1 (modulo n) musí být první na řadě.
        pairs = get_the_houmwrk(homeworks, k=2, seed=123)
        
        # Extrahujeme zamíchané pořadí z výsledku
        shuffled_order = [reviewer for reviewer, _ in pairs]
        
        for i, (reviewer, to_review) in enumerate(pairs):
            # První přiřazený úkol musí být ten hned za ním v zamíchaném poli
            expected_first = shuffled_order[(i + 1) % 3]
            expected_second = shuffled_order[(i + 2) % 3]
            
            self.assertEqual(to_review[0], expected_first)
            self.assertEqual(to_review[1], expected_second)