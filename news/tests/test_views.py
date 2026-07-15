from django.urls import reverse

from hw.tests.setUp import BaseHWTestCase


class TestNewsPostView(BaseHWTestCase):
   def test_view_post_200(self):
        self.assert_get_200(self.student, "news-post", template_name="newspost/posts.html")
   def test_view_create_post_200(self):
        self.assert_get_200(self.superuser, "create-news-post", template_name="newspost/create_post.html")
   def test_view_edit_post_200(self):
        self.assert_get_200(self.superuser, "edit-news-post", template_name="newspost/edit_post.html", pk=self.news_post.pk)
        
   def test_view_create_post_404(self):
          self.assert_get_404(self.student, "create-news-post")
          self.assert_get_404(self.teacher, "create-news-post")
          
   def test_view_POST_create_post(self):
        f_data={
            "announcement":"AAAAAA",}
        self.client.force_login(self.superuser)
        url=reverse("create-news-post")
        response=self.client.post(url, f_data)
        self.assertEqual(response.status_code,302)
     