from django.test import TestCase
from accounts.forms import CustomUserChangeForm, CustomUserCreationForm

class TestFormsCorrect(TestCase):
     def test_edit_form(self):
        form_data = {
             "username":"ahoj",
            "email":"g@f.cz",
            "first_name":"Derek",
            "surname":"Derekk",
            "tel":"+420 212 345 678"
            }
        form = CustomUserChangeForm(data=form_data)
        self.assertTrue(form.is_valid())
        
     def test_create_form(self):
          form_data={
               "username":"jmeno",
               "email":"g@w.cz",
               "first_name":"Ddferek",
               "surname":"Defrekk",
               "tel":"+420 312 345 678",
               "password1":"StrongPass123!",
               "password2":"StrongPass123!",
          }
          form=CustomUserCreationForm(data=form_data)
          self.assertTrue(form.is_valid())
          
class TestFormWrong(TestCase):
     def test_edit_form_not_filled_collum(self):
          form_data = {
            "email":"g@f.cz",
            "first_name":"Derek",
            "surname":"Derekk",
            "tel":"+420 212 345 678"
            }
          form = CustomUserChangeForm(data=form_data)
          self.assertFalse(form.is_valid())
          # když se nevyplní kononka, vyplnila by se starou hodnotou?????
     