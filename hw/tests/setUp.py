from django.test import TestCase, override_settings
from django.urls import reverse
from hw.models import Subject, Assignment, Key, Homework, HomeworkStudentComment, CodeFile
from accounts.models import CustomUser, SubjectType
from django.utils import timezone
from datetime import timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from news.models import NewsPost

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
        
        self.superuser = CustomUser.objects.create_superuser(
            username="admin",
            password="pass",
            first_name="Ilja",
            surname="Jakovenku",
        )
        
        self.news_post = NewsPost.objects.create(
            announcement="pog",
               date=timezone.now(),)
        
        
    def assert_get_200(self, user, url_name, template_name=None, **kwargs):
        self.client.force_login(user)
        url_kwargs = {}
        if 'pk' in kwargs:
            url_kwargs['pk'] = kwargs.pop('pk')
        url = url = reverse(url_name, kwargs=url_kwargs)
        response = self.client.get(url, data=kwargs)
        self.assertEqual(response.status_code, 200)
        if template_name:
                self.assertTemplateUsed(response, template_name)
                
    def assert_get_403(self, user, url_name, **kwargs):
        """
        Pomocná metoda ověřující, že uživatel dostane korektní HTTP status 403.
        """
        self.client.force_login(user)
        url = reverse(url_name, kwargs=kwargs)
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 403)
    def assert_get_404(self, user, url_name, **kwargs):
        """
        Pomocná metoda ověřující, že uživatel dostane korektní HTTP status 404.
        """
        self.client.force_login(user)
        url = reverse(url_name, kwargs=kwargs)
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)