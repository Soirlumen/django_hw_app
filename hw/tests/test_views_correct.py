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

class HWViewStatus200Tests(BaseHWTestCase):

    def assert_get_200(self, user, url_name, **kwargs):
        self.client.force_login(user)
        response = self.client.get(reverse(url_name, kwargs=kwargs))
        self.assertEqual(response.status_code, 200)

    def test_list_active_200(self):
        self.assert_get_200(self.student, "list_active")

    def test_list_after_deadline_200(self):
        self.assert_get_200(self.student, "list_after_deadline")

    def test_list_before_release_200_teacher(self):
        self.assert_get_200(self.teacher, "list_before_release")

    def test_assignment_teacher_detail_200(self):
        self.assert_get_200(
            self.teacher,
            "assgn_detail_teacher",
            pk=self.assignment.pk,
        )

    def test_assignment_student_detail_200(self):
        self.assert_get_200(
            self.student,
            "assgn_detail_student",
            pk=self.assignment.pk,
        )

    def test_assignment_create_200(self):
        self.assert_get_200(self.teacher, "assignment_create")

    def test_homework_submit_200(self):
        self.client.force_login(self.student)
        response = self.client.get(
            reverse("hw_submit"),
            {"assgn_id": self.assignment2.pk},
        )
        self.assertEqual(response.status_code, 200)

    def test_homework_update_200(self):
        self.assert_get_200(
            self.student,
            "homework_update",
            pk=self.homework.pk,
        )

    def test_assignment_delete_confirm_200(self):
        self.assert_get_200(
            self.teacher,
            "assignment_delete",
            pk=self.assignment.pk,
        )

    def test_homework_detail_student_200(self):
        self.assert_get_200(
            self.student,
            "hw_detail",
            pk=self.homework.pk,
        )

    def test_homework_detail_teacher_200(self):
        self.assert_get_200(
            self.teacher,
            "hw_detail",
            pk=self.homework.pk,
        )

    def test_evaluation_edit_200(self):
        self.assert_get_200(
            self.teacher,
            "evaluate_edit",
            pk=self.homework.pk,
        )

    def test_evaluation_delete_200(self):
        self.assert_get_200(
            self.teacher,
            "evaluate_delete",
            pk=self.homework.pk,
        )

    def test_student_comment_list_200(self):
        self.assert_get_200(self.student, "student_comment_list")

    def test_student_comment_detail_200(self):
        self.assert_get_200(
            self.student,
            "student_comment_detail",
            pk=self.studentComment2.pk,
        )

    def test_received_comment_detail_200(self):
        self.assert_get_200(
            self.student,
            "student_received_comment_detail",
            pk=self.studentComment.pk,
        )

    def test_teacher_comments_list_200(self):
        self.assert_get_200(self.teacher, "teacher_comments_list")