import django_filters
from .models import Assignment
class AssignmentTFilter(django_filters.FilterSet):
     class Meta:
          model = Assignment
          fields = {
               'subject':["exact"]
          }
     def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.filters["subject"].queryset = user.teacher_subjects
          
class AssignmentSFilter(django_filters.FilterSet):
     class Meta:
          model = Assignment
          fields = {
               'subject':["exact"]
          }
     def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user:
            self.filters["subject"].queryset = user.student_subjects
     
# class HomeworkCommentsFilter(django_filters.FilterSet):
#      class Meta:
#           model=HomeworkStudentComment
#           fields={
#                "reviewer":["exact",],
#                   }