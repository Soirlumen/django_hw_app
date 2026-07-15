from hw.tests.setUp import BaseHWTestCase

class TestPages200(BaseHWTestCase):
     def test_profile_view(self):
          self.assertTrue(self.client.login(username="teacher", password="pass"))
          response=self.client.get("/cs/profile/")
          self.assertEqual(response.status_code,200)
     def test_dashboard_view(self):
          self.assertTrue(self.client.login(username="teacher", password="pass"))
          response=self.client.get("/cs/")
          self.assertEqual(response.status_code,200)
     def test_login_view_unlogged(self):
          response=self.client.get("/cs/accounts/login/")
          self.assertEqual(response.status_code,200)
          
class TestPagesBadAccess(BaseHWTestCase):
     def test_dashboard_view_logout(self):
          response=self.client.get("/")
          self.assertEqual(response.status_code,302) #redirect
     def test_page_not_found(self):
          response=self.client.get("/yksdjbgkjsd/") #neexistující stránka
          self.assertEqual(response.status_code,404)
     def test_login_view_logged(self):
          self.assertTrue(self.client.login(username="teacher", password="pass"))
          response=self.client.get("/cs/accounts/login/")
          self.assertEqual(response.status_code,302) #redirect na stránku pro přihlášené!
