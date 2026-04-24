from django.utils import timezone
from .setUp import BaseHWTestCase
from django.urls import reverse

class TestPages(BaseHWTestCase):
   def test_homepage_status_code(self):
      self.assertTrue(self.client.login(username="teacher", password="pass"))
      response=self.client.get('/cs/')
      self.assertEqual(response.status_code, 200)
   def test_anonymous_redirected(self):
      response = self.client.get('/cs/')
      self.assertIn(response.status_code, [302, 403])
   def test_teacher_list_before_release(self):
      self.assertTrue(self.client.login(username="teacher", password="pass"))
      response=self.client.get("/cs/hw/list/before_release/")
      self.assertEqual(response.status_code,200)
   def test_list_active(self):
      self.assertTrue(self.client.login(username="teacher", password="pass"))
      response=self.client.get("/cs/hw/list/active/")
      self.assertEqual(response.status_code,200)
   def test_after_deadline(self):
      self.assertTrue(self.client.login(username="teacher", password="pass"))
      response=self.client.get("/cs/hw/list/after_deadline/")
      self.assertEqual(response.status_code,200) 
   def test_assignment_detail_teacher(self):
      self.assertTrue(self.client.login(username="teacher", password="pass"))
      response=self.client.get(reverse("assgn_detail_teacher", kwargs={"pk":self.assignment.pk}))
      self.assertEqual(response.status_code,200)      
   def test_assignment_detail_student(self):
      self.assertTrue(self.client.login(username="student", password="pass"))
      response=self.client.get(reverse('assgn_detail_student', kwargs={'pk': self.assignment.pk}))
      self.assertEqual(response.status_code,200)      
   def test_create_assignment(self):
      self.assertTrue(self.client.login(username="teacher", password="pass"))
      response=self.client.get("/cs/hw/homework/createass/")
      self.assertEqual(response.status_code,200)      
   def test_show_homework(self):
      self.assertTrue(self.client.login(username="student", password="pass"))
      response=self.client.get(reverse("hw_detail",kwargs={"pk":self.homework.pk}))
      self.assertEqual(response.status_code,200)  
   def test_student_comment_list_view(self):
      self.assertTrue(self.client.login(username="student", password="pass"))
      response=self.client.get(reverse("student_comment_list"))
      self.assertTrue(response.status_code,200)
   def test_student_comment_detail_view(self):
      self.assertTrue(self.client.login(username="student", password="pass"))
      response=self.client.get(reverse("student_comment_detail",kwargs={"pk":self.studentComment2.pk}))
      self.assertTrue(response.status_code,200)
      self.assertTemplateUsed(response,"student_comments/detail.html")
   def test_student_received_comment_detail_view(self):
      self.assertTrue(self.client.login(username="student2", password="pass"))
      response=self.client.get(reverse("received_comment_detail",kwargs={"pk":self.studentComment2.pk}))
      self.assertEqual(response.status_code,200)
      self.assertTemplateUsed(response,"student_comments/received_detail.html")
   def test_teacher_list_after_deadline_view(self):
        self.assertTrue(self.client.login(username="teacher", password="pass"))
        response = self.client.get(reverse("list_after_deadline"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('filter_t', response.context)
   def test_student_cannot_remove_file_after_deadline(self):
        """Student nesmí smazat soubor, pokud už uplynul deadline."""
        self.assertTrue(self.client.login(username="student", password="pass"))
        # Nastavíme úkolu deadline do minulosti pro tento test
        self.assignment.deadline = timezone.now() - timezone.timedelta(days=1)
        self.assignment.save()
        
        url = reverse("homework_file_remove", kwargs={
            "hw_pk": self.homework.pk, 
            "file_pk": self.codefile.pk # předpokládám, že v setUp máš self.codefile
        })
        response = self.client.post(url) # file_remove vyžaduje POST
        self.assertRedirects(response, self.homework.get_assgn_student_url())
        # Zkontrolujeme, že se v messages objevila chyba
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("Po deadline" in str(m) for m in messages))
      