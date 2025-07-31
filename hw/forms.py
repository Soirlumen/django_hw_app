from django import forms
from .models import Homework, Assignment


class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = ("engrossment",)


class AssignmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(AssignmentForm, self).__init__(*args, **kwargs)
        if self.user and hasattr(self.user, "teacher_profile"):
            self.fields["subject"].queryset = self.user.teacher_profile.subjects.all()

    class Meta:
        model = Assignment
        fields = ("title", "subject", "description", "release", "deadline", "max_score")
        widgets = {
            "deadline": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "release": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = ("text_evaluation", "score")
