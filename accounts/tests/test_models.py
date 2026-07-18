from hw.tests.setUp import BaseHWTestCase
from django.db import IntegrityError
from accounts.models import SubjectType


class CustomSubjectTypeTestCase(BaseHWTestCase):

     def test_duplicate_user_subject_assignment_fails(self):
        with self.assertRaises(IntegrityError):
            SubjectType.objects.create(
                user=self.teacher, 
                subject=self.subject, 
                role="teacher"
            )
     def test_duplicate_user_subject_assignment_with_different_role_fails(self):
        with self.assertRaises(IntegrityError):
            SubjectType.objects.create(
                user=self.teacher, 
                subject=self.subject, 
                role="student"
            )
            
     def test_property_methods(self):
        self.assertEqual(self.teacher.is_teacher, True)
        self.assertEqual(self.teacher.is_student, False)
        self.assertEqual(self.student.is_student, True)
        self.assertEqual(self.teacher.teacher_subjects.count(), 1)
     def test_subjecttype_to_str(self):
        subject_type = SubjectType.objects.get(user=self.teacher, subject=self.subject)
        expected_str = f"{self.teacher.username} - {self.subject} ({subject_type.role})"
        self.assertEqual(str(subject_type), expected_str)