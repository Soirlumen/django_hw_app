from .setUp import BaseHWTestCase
from hw.models import HomeworkStudentComment
from django.urls import reverse

class TestForms(BaseHWTestCase):
     def test_HomeworkStudentCommentForm_valid(self):
          self.assertTrue(self.client.login(username="student", password="pass"))
          form_data={
               'comment':'nic moc',
          }
          response=self.client.post(reverse("student_comment_detail",kwargs={"pk":self.studentComment2.pk}),data=form_data)
          self.assertEqual(response.status_code,302)
          self.assertTrue(HomeworkStudentComment.objects.filter(comment='nic moc').exists())