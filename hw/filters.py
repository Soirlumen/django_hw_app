import django_filters
from .models import Assignment, Homework, HomeworkStudentComment

class AssignmentFilter(django_filters.FilterSet):
     subject__name=django_filters.CharFilter(lookup_expr='icontains')
     class Meta:
          model = Assignment
          fields = ['subject',]
     
