from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import timedelta
from hw.models import Key, Homework, Assignment
from .setUp import BaseHWTestCase 
class HomeworkCreateIntegrationTest(BaseHWTestCase):

     def test_successful_homework_submission_flow(self):
          """
          Student odevzdává úkol k novému zadání.
          """
          new_assignment = Assignment.objects.create(
               title="Suprzadání",
               subject=self.subject,
               teacher=self.teacher,
               description="fakt bengr",
               max_score=10,
               release=timezone.now() - timedelta(days=1),
               deadline=timezone.now() + timedelta(days=1),
          )

          self.assert_get_200(
               user=self.student, 
               url_name='hw_create', 
               template_name='homework/hw_create.html',
               assgn_id=new_assignment.pk
          )

          # Krok 2: Příprava POST dat
          test_file = SimpleUploadedFile("reseni.py", b"print('Ahoj')", content_type="text/x-python")
          form_data = {
               'programming_language': 'python',
               'engrossment': 'def main():\n    print("Hotovo")',
               'notes': 'Moje poznámka',
               'filesimput': [test_file]
          }

          # Krok 3: Odeslání POST požadavku
          self.client.force_login(self.student)
          url = f"{reverse('hw_create')}?assgn_id={new_assignment.pk}"
          response = self.client.post(url, data=form_data, follow=True)

          # Krok 4: Ověření úspěšného přesměrování na detail pro studenta
          expected_redirect_url = reverse('assgn_detail_student', kwargs={'pk': new_assignment.pk})
          self.assertRedirects(response, expected_redirect_url)

          # Krok 5: Ověření databáze
          # views.py automaticky najde nebo vytvoří Key
          student_key = Key.objects.get(student=self.student, assignment=new_assignment)
          homework = Homework.objects.get(key=student_key)
          
          self.assertEqual(homework.programming_language, 'python')
          self.assertEqual(homework.engrossment, 'def main():\n    print("Hotovo")')
          self.assertEqual(homework.files.count(), 1)

     def test_homework_submission_fails_after_deadline(self):
          """Ověření, že po termínu (deadline) formulář vyhodí chybu (stav 200 s chybou)."""
          # Vytvoříme nové zadání, které je již po deadline
          belated_assignment = Assignment.objects.create(
               title="Úkol po deadline",
               subject=self.subject,
               teacher=self.teacher,
               description="Zadání",
               max_score=10,
               release=timezone.now() - timedelta(days=2),
               deadline=timezone.now() - timedelta(hours=1),  # Už hodinu po deadline
          )

          self.client.force_login(self.student)
          url = f"{reverse('hw_create')}?assgn_id={belated_assignment.pk}"
          
          form_data = {
               'programming_language': 'python',
               'engrossment': 'print("Pozdě")',
          }

          response = self.client.post(url, data=form_data)

          # Formulář neprojde validací v clean(), takže view neprovede redirect, ale vrátí stav 200
          self.assertEqual(response.status_code, 200)
          
          # Ověříme, že v DB pro tento Key NEEXISTUJE žádný Homework
          student_key = Key.objects.get(student=self.student, assignment=belated_assignment)
          self.assertFalse(Homework.objects.filter(key=student_key).exists())

     def test_homework_submission_fails_when_already_submitted(self):
          """Ověření, že pokud už student úkol odevzdal, view ho nepustí a přesměruje (302)."""
          # Použijeme self.assignment z BaseHWTestCase, kde už self.homework existuje
          target_assignment = self.assignment

          self.client.force_login(self.student)
          url = f"{reverse('hw_create')}?assgn_id={target_assignment.pk}"
          
          form_data = {
               'programming_language': 'python',
               'engrossment': 'Druhý pokus, který má selhat',
          }

          response = self.client.post(url, data=form_data)
          
          # Podle vaší implementace ve views.py to rovnou vrací redirect (302) na detail úkolu
          self.assertEqual(response.status_code, 302)
          
          # Ověříme, že byl přesměrován na správnou adresu (get_assgn_student_url)
          expected_url = self.homework.get_assgn_student_url()
          self.assertRedirects(response, expected_url, fetch_redirect_response=False)
          
          # V databázi musí stále zůstat pouze 1 původní úkol
          self.assertEqual(Homework.objects.filter(key=self.key).count(), 1)
          