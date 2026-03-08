from django import forms
from .models import Homework, Assignment, HomeworkStudentComment
from django.core.exceptions import ValidationError
from django.utils import timezone
# from crispy_forms.helper import FormHelper
# from crispy_forms.layout import Layout, Field, HTML
# from crispy_forms.bootstrap import AppendedText
from django.utils.safestring import mark_safe
from .widgets import CodeMirrorWidget
from django.conf import settings

UPLOAD_HELP_TEXT = (
    f"Můžete přiložit více souborů najednou. "
    f"Maximálně {settings.MAX_UPLOAD_FILES_NUMBER} souborů, "
    f"každý nejvýše {settings.MAX_UPLOAD_FILE_SIZE_MB} MB."
)
 
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        max_size=settings.MAX_UPLOAD_FILE_SIZE
        max_size_mb = max_size/(1024**2)
        max_files=settings.MAX_UPLOAD_FILES_NUMBER
        if not data:
            return []

        if isinstance(data, (list, tuple)):
            files = [single_file_clean(d, initial) for d in data]
        else:
            files = [single_file_clean(data, initial)]
        if len(files) > max_files:
            raise ValidationError(
                f"Najednou můžeš nahrát maximálně {max_files} souborů."
            )

        for f in files:
            if f.size > max_size:
                raise ValidationError(
                    f"Soubor '{f}' je příliš velký. Maximum je {max_size_mb:.0f} MB."
                )
        return files

#vytvoření úkolu
class CreateHomeworkForm(forms.ModelForm):
    max_size=settings.MAX_UPLOAD_FILE_SIZE/(1024**2)
    filesimput= MultipleFileField(help_text=UPLOAD_HELP_TEXT ,required=False, label="Upload files")
    def clean(self):
        cleaned_data=super().clean()
        submitted=cleaned_data.get("submitted")
        if submitted is None:
            return cleaned_data
        deadline=self.instance.key.assignment.deadline
        if timezone.now() > deadline:
            raise ValidationError("Nemůžeš odevzdat úkol po deadline!")
        return cleaned_data     
    class Meta:
        model = Homework
        fields = ("programming_language","engrossment",)
        widgets= {
            "engrossment": CodeMirrorWidget()
        }

# úprava úkolu  
class HomeworkForm(forms.ModelForm):
    max_size=settings.MAX_UPLOAD_FILE_SIZE/(1024**2)
    filesimput= MultipleFileField(help_text=UPLOAD_HELP_TEXT ,required=False, label="Upload files")
    
    def clean(self):
        cleaned_data = super().clean()
        deadline = self.instance.key.assignment.deadline

        if timezone.now() > deadline:
            raise ValidationError("Nemůžeš odevzdat úkol po deadline!")

        new_files = cleaned_data.get("filesimput", [])
        current_files_count = self.instance.files.count() if self.instance.pk else 0
        #nepřerkočit max nahraných souborů
        if current_files_count + len(new_files) > settings.MAX_UPLOAD_FILES_NUMBER:
            raise ValidationError(
                f"Celkem může být u odevzdání maximálně "
                f"{settings.MAX_UPLOAD_FILES_NUMBER} souborů."
            )
        return cleaned_data
 
    class Meta:
        model = Homework
        fields = ("programming_language","engrossment",)
        widgets= {
            "engrossment": CodeMirrorWidget()
        }
          
#vytvoření zadání úkolu
class AssignmentForm(forms.ModelForm):
    max_size=settings.MAX_UPLOAD_FILE_SIZE/(1024**2)
    filesimput= MultipleFileField(help_text=UPLOAD_HELP_TEXT ,required=False, label="Upload files")
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(AssignmentForm, self).__init__(*args, **kwargs)
        if self.user:
            self.fields["subject"].queryset = self.user.teacher_subjects
            self.fields["description"].help_text= mark_safe("Popište zadání domácího úkolu. Podporuje <a href='https://www.daringfireball.net/projects/markdown/syntax'>Markdown syntax</a>.")
        
    def clean_subject(self):
        subject = self.cleaned_data["subject"]
        if self.user and not subject.subject_type.filter(user=self.user, role="teacher").exists():
            raise forms.ValidationError("Na tomto předmětu nejsi veden jako učitel.")
        return subject
    def clean(self):
        cleaned_data = super().clean()
        new_files = cleaned_data.get("filesimput", [])

        if len(new_files) > settings.MAX_UPLOAD_FILES_NUMBER:
            raise ValidationError(
                f"Můžeš přiložit maximálně {settings.MAX_UPLOAD_FILES_NUMBER} souborů."
            )

        return cleaned_data

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
        fields = ["score","text_evaluation", ]
                
    def clean_score(self):
        score = self.cleaned_data.get("score")
        maxscore = self.instance.key.assignment.max_score
        
        if score is not None and score > maxscore:
            raise ValidationError(f"max score je {maxscore}")
        return score
    
    # aby mohl učitel zadat maximálně max_score bodů
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['score'].widget.attrs.update({
            'min': 0,
            'max': self.instance.key.assignment.max_score, 

        })
        self.fields["score"].help_text = (f"Maximální počet bodů je  {self.instance.key.assignment.max_score}")
        self.fields["text_evaluation"].help_text= mark_safe("Ohodnoťte úkol. Podporuje <a href='https://www.daringfireball.net/projects/markdown/syntax'>Markdown syntax</a>.")
    
# pro vyplnění komentu
class HomeworkStudentCommentForm(forms.ModelForm):
    class Meta:
        model=HomeworkStudentComment
        fields=("comment",)
        widgets = {
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 6, "placeholder": "Napiš zpětnou vazbu..."}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["comment"].help_text= mark_safe("Podporuje <a href='https://www.daringfireball.net/projects/markdown/syntax'>Markdown syntax</a>.")
    

# generování k-tic hodnotících k úkolu
class MakeCommentsForm(forms.Form):
    k=forms.IntegerField(min_value=1)
