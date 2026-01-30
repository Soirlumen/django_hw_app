from .setUp import BaseHWTestCase

class TestPages(BaseHWTestCase):
   def test_homepage_status_code(self):
      self.assertTrue(self.client.login(username="teacher", password="pass"))
      response=self.client.get('/')
      self.assertEqual(response.status_code, 200)
   def test_anonymous_redirected(self):
      response = self.client.get('/')
      self.assertIn(response.status_code, [302, 403])
   def test_teacher_list_before_release(self):
      self.assertTrue(self.client.login(username="teacher", password="pass"))
      response=self.client.get("/hw/list/before_release/")
      self.assertEqual(response.status_code,200)
   def test_list_active(self):
      self.assertTrue(self.client.login(username="teacher", password="pass"))
      response=self.client.get("/hw/list/active/")
      self.assertEqual(response.status_code,200)