from django.test import TestCase, override_settings
from hw.models import Subject, Assignment, Key, Homework, HomeworkStudentComment, CodeFile
from accounts.models import CustomUser, SubjectType
from django.utils import timezone
from datetime import timedelta
from django.core.files.uploadedfile import SimpleUploadedFile

@override_settings(DEFAULT_FILE_STORAGE='django.core.files.storage.InMemoryStorage')
class BaseHWTestCase(TestCase):
    def setUp(self):
        self.teacher = CustomUser.objects.create_user(
            username="teacher",
            password="pass",
            first_name="Adam",
            surname="Břídil",
        )
        self.student = CustomUser.objects.create_user(
            username="student",
            password="pass",
            first_name="Daniela",
            surname="Hušhuš",
        )
        self.student2 = CustomUser.objects.create_user(
            username="student2",
            password="pass",
            first_name="Vojta",
            surname="Lustr",
        )

        self.subject = Subject.objects.create(
            name="pgr2",
            year=2026 
        )
        SubjectType.objects.create(user=self.teacher, subject=self.subject, role="teacher")
        SubjectType.objects.create(user=self.student, subject=self.subject, role="student")
        SubjectType.objects.create(user=self.student2, subject=self.subject, role="student")

        now = timezone.now()
        fake_file = SimpleUploadedFile("test_code.py", b"print('hello world')")
        self.codefile = CodeFile.objects.create(
            file=fake_file
        )
        
        self.codefile._upload_user = self.teacher
        self.codefile._upload_assignment = None 

        self.assignment = Assignment.objects.create(
            title="Domácí úkol 1",
            subject=self.subject,
            teacher=self.teacher,
            description="Testovací zadání",
            max_score=10,
            release=now - timedelta(days=1),
            deadline=now + timedelta(days=1),
        )
        self.assignment.files.add(self.codefile)
        self.key = Key.objects.create(student=self.student, assignment=self.assignment)
        self.key2 = Key.objects.create(student=self.student2, assignment=self.assignment)
        self.homework = Homework.objects.create(
            key=self.key,
            engrossment="Testovací odevzdaný úkol",
            submitted=now,
        )
        
        self.assignment_before_release = Assignment.objects.create(
            title="Domácí úkol před zveřejněním",
            subject=self.subject,
            teacher=self.teacher,
            description="Testovací zadání",
            max_score=10,
            release=now + timedelta(days=1),
            deadline=now + timedelta(days=2),
        )
        
        self.homework.files.add(self.codefile)

        self.homework2 = Homework.objects.create(
            key=self.key2,
            engrossment="Testovací odevzdaný úkol2",
            submitted=now,
        )
        self.studentComment = HomeworkStudentComment.objects.create(
            hw=self.homework,
            reviewer=self.student2,
            comment="ahoj",
        )
        self.studentComment2 = HomeworkStudentComment.objects.create(
            hw=self.homework2,
            reviewer=self.student,
            comment="", 
        )
        self.assignment2 = Assignment.objects.create(
            title="DCv",
            subject=self.subject,
            teacher=self.teacher,
            description="Domácí cvičení",
            max_score=10,
            release=now - timedelta(days=1),
            deadline=now + timedelta(days=1),
        )
        
        self.key3 = Key.objects.create(student=self.student, assignment=self.assignment2)
        self.key4 = Key.objects.create(student=self.student2, assignment=self.assignment2)
        
        self.homework3 = Homework.objects.create(
            key=self.key3,
            engrossment="Testovací odevzdaný úkol2",
            submitted=now,
        )
    