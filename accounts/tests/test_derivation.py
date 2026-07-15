# integration tests
from hw.tests.setUp import BaseHWTestCase
from django.urls import reverse

class TestLoginFlow(BaseHWTestCase):
    def test_successful_login_logout_flow(self):
        profile_url = reverse("profile")
        # nepřihlášený uživatel se pokusí dostat na profil
        response = self.client.get(profile_url)
        redirect_target = response.headers.get('Location', '')
        
        self.assertIn("login", redirect_target)
        self.assertIn("next=", redirect_target)
        self.assertIn("profile", redirect_target)

        # přihlášení
        login_url = reverse("login")
        login_response = self.client.post(
            login_url, 
            {"username": "teacher", 
             "password": "pass"}
        )
        self.assertEqual(login_response.status_code, 302)
        
        # success_login_view je přístupné
        success_url = reverse("success_login")
        success_response = self.client.get(success_url)
        
        self.assertEqual(success_response.status_code, 200)
        self.assertTemplateUsed(success_response, "accounts/success_login.html")
        
        logout_url = reverse("logout")
        logout_response = self.client.post(logout_url)
        
        self.assertEqual(logout_response.status_code, 302)
        
        logout_redirect_target = logout_response.headers.get('Location', '')
        self.assertIn("login", logout_redirect_target)

        # po odhlášení už nedostaneš zpět na profil
        final_profile_response = self.client.get(profile_url)
        self.assertEqual(final_profile_response.status_code, 302)