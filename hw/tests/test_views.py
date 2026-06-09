from .setUp import BaseHWTestCase
from django.urls import reverse
from hw.models import Assignment

class TestHWViewStatus200(BaseHWTestCase):
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

    def test_list_active_200(self):
        self.assert_get_200(self.teacher, "list_active", template_name="list/active.html")

    def test_list_after_deadline_200(self):
        self.assert_get_200(self.teacher, "list_after_deadline", template_name="list/after_deadline.html")

    def test_list_active_S_200(self):
        self.assert_get_200(self.student, "list_active", template_name="list/active.html")

    def test_list_after_deadline_s_200(self):
        self.assert_get_200(self.student, "list_after_deadline", template_name="list/after_deadline.html")

    def test_list_before_release_200_teacher(self):
        self.assert_get_200(self.teacher, "list_before_release", template_name="list/before_release.html")

    def test_assignment_teacher_detail_200(self):
        self.assert_get_200(self.teacher,"assgn_detail_teacher",template_name="homework/teacher_detail.html",pk=self.assignment.pk)

    def test_assignment_student_detail_200(self):
        self.assert_get_200(self.student, "assgn_detail_student", template_name="homework/student_detail.html",pk=self.assignment.pk,)

    def test_assignment_create_200(self):
        self.assert_get_200(self.teacher, "ass_create", template_name="homework/ass_create.html")

    def test_assignment_delete_200(self):
        self.assert_get_200(self.teacher, "assignment_delete", pk=self.assignment.pk, template_name="homework/ass_delete_confirm.html")

    def test_assignenment_edit_200(self):
        self.assert_get_200(self.teacher, "assgn_edit",template_name="homework/as_update.html", pk=self.assignment.pk)

    def test_homework_update_200(self):
        self.assert_get_200(self.student,"homework_update", template_name="homework/hw_update.html",pk=self.homework.pk)

    def test_homework_create_view_200(self):
        self.assert_get_200(self.student2, "hw_create", template_name="homework/hw_create.html", assgn_id=self.assignment2.pk)

    def test_homework_detail_student_200(self):
        self.assert_get_200(self.student,"hw_detail",template_name="homework/hw_detail.html",pk=self.homework.pk)

    def test_homework_detail_teacher_200(self):
        self.assert_get_200(self.teacher, "hw_detail", template_name="homework/hw_detail.html", pk=self.homework.pk)

    def test_evaluation_edit_200(self):
        self.assert_get_200(self.teacher, "evaluate_edit", template_name="homework/hw_evaluation_update.html", pk=self.homework.pk)

    def test_evaluation_delete_200(self):
        self.assert_get_200(self.teacher,"evaluate_delete", template_name="homework/hw_evaluation_delete_confirm.html",pk=self.homework.pk)

    def test_student_comment_list_200(self):
        self.assert_get_200(self.student, "student_comment_list", template_name="student_comments/reviewer_list.html")

    def test_student_comment_detail_s_200(self):
        self.assert_get_200(self.student, "reviewer_form", template_name="student_comments/reviewer_form.html", pk=self.studentComment2.pk)

    def test_received_comment_detail_200(self):
        self.assert_get_200(self.teacher,"comment_feedback_detail", template_name="student_comments/feedback_detail.html",pk=self.studentComment.pk,)
    
    def test_received_comment_detail_s_200(self):
        self.assert_get_200(self.student,"comment_feedback_detail", template_name="student_comments/feedback_detail.html",pk=self.studentComment.pk,)

    def test_teacher_comments_list_200(self):
        self.assert_get_200(self.teacher, "teacher_comment_list", template_name="student_comments/teacher_list.html")
        
class TestHWViewStatus403(BaseHWTestCase):
    def assert_get_403(self, user, url_name, **kwargs):
        self.client.force_login(user)
        response = self.client.get(reverse(url_name, kwargs=kwargs))
        self.assertEqual(response.status_code, 403)

    def test_list_before_release_403_student(self):
        self.assert_get_403(self.student, "list_before_release")

    def test_assignment_teacher_detail_403_student(self):
        self.assert_get_403(self.student,"assgn_detail_teacher",pk=self.assignment.pk)

    def test_assignment_create_403_student(self):
        self.assert_get_403(self.student,"ass_create")
    def test_assignment_edit_403_student(self):
        self.assert_get_403(self.student,"assgn_edit",pk=self.assignment.pk)
        
    def test_student_cannot_access_assignment_before_release_403(self):
        self.assert_get_403(self.student,"assgn_detail_student",pk=self.assignment_before_release.pk)
        
class TestViewPOST(BaseHWTestCase):
    def test_assignment_delete_POST(self):
        self.client.force_login(self.teacher)
        url=reverse("assignment_delete",kwargs={'pk':self.assignment.pk})
        response=self.client.post(url)
        self.assertEqual(response.status_code,302)
        self.assertFalse(Assignment.objects.filter(pk=self.assignment.pk).exists())
