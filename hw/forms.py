from django import forms
from .models import Homework, Assignment, HomeworkStudentComment
from django.core.exceptions import ValidationError
from django.utils import timezone

#vytvoření úkolu
class CreateHomeworkForm(forms.ModelForm):
    def clean(self):
        cleaned_data=super().clean()
        submitted=cleaned_data.get("submitted")
        if submitted is None:
            return submitted
        deadline=self.instance.key.assignment.deadline
        if timezone.now() > deadline:
            raise ValidationError("Nemůžeš odevzdat úkol po deadline!")
        return submitted     
    class Meta:
        model = Homework
        fields = ("engrossment",)
# úprava úkolu  
class HomeworkForm(forms.ModelForm):
    def clean(self):
        cleaned_data=super().clean()
        submitted=cleaned_data.get("submitted")
        # if submitted is None:
        #     return submitted
        deadline=self.instance.key.assignment.deadline
        if timezone.now() > deadline:
            raise ValidationError("Nemůžeš odevzdat úkol po deadline!")
        return submitted     
    class Meta:
        model = Homework
        fields = ("engrossment",)
          
#vytvoření zadání úkolu
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
#vyplnění hodnocení od učitele
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
    
# pro vyplnění komentu
class HomeworkStudentCommentForm(forms.ModelForm):
    class Meta:
        model=HomeworkStudentComment
        fields=("comment",)
        widgets = {
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 6, "placeholder": "Napiš zpětnou vazbu..."}),
        }

# generování k-tic hodnotících k úkolu
class MakeCommentsForm(forms.Form):
    k=forms.IntegerField(min_value=1)