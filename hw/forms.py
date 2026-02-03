from django import forms
from .models import Homework, Assignment, HomeworkStudentComment
from django.core.exceptions import ValidationError

class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = ("engrossment",)


class AssignmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(AssignmentForm, self).__init__(*args, **kwargs)
        if self.user:
            self.fields["subject"].queryset = self.user.teacher_subjects
        
    def clean_subject(self):
        subject = self.cleaned_data["subject"]
        if self.user and not subject.subject_type.filter(user=self.user, role="teacher").exists():
            raise forms.ValidationError("Na tomto předmětu nejsi veden jako učitel.")
        return subject

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

    def clean_score(self):
        score = self.cleaned_data.get("score")
        maxscore = self.instance.key.assignment.max_score

        if score is not None and score > maxscore:
            raise ValidationError(f"max score je {maxscore}")
        return score
    
class HomeworkStudentCommentForm(forms.ModelForm):
    class Meta:
        model=HomeworkStudentComment
        fields=("comment",)

'''dobře takže,
form se zeptá, kolik člověk dostane úkolů na opravení
form provede funkci míchání a přidělení lidí k úkolu
ve views se vyberou jen ti lidi, kdo v daný moment budou mít odevzdaný úkol, ten se passne do form(?)
ve for cyklu bude vytvářet recordy
pokud bude chtít učitel víc commentů na úkol, než n-1, vyhodí validation error a nic se nevytvoří
chci se zabít
'''
class MakeComments(forms.ModelForm):
    number_of_reviewer=forms.IntegerField(min_value=1)
        
        
