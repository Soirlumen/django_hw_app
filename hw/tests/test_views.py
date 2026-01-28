from .setUp import BaseHWTestCase

class TestPages(BaseHWTestCase):
     def test_homepage_status_code(self):
        self.assertTrue(self.client.login(username="teacher", password="pass"))
        response=self.client.get('/')
        self.assertEqual(response.status_code, 200)
     def test_anonymous_redirected(self):
        response = self.client.get('/')
        self.assertIn(response.status_code, [302, 403])
