from django import forms
from .models import Homework, Assignment


class HomeworkForm(forms.ModelForm):
    class Meta:
        model=Homework
        fields=("engrossment",)

class AssignmentForm(forms.ModelForm):
    class Meta:
        model=Assignment
        fields=("title","subject","description","release","deadline",)
        widgets = {
            'deadline': forms.DateTimeInput(attrs={
                'type': 'datetime-local'
            }),
            'release': forms.DateTimeInput(attrs={
                'type': 'datetime-local'
            })
        }

class EvaluationForm(forms.ModelForm):
    class Meta:
        model=Homework
        fields=("text_evaluation","score")