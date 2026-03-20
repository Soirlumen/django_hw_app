from django import forms
from .models import Homework, Assignment, HomeworkStudentComment
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.html import format_html
from django.utils.functional import lazy
from .widgets import CodeMirrorWidget
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):

        kwargs.setdefault("label", _("Přiložit soubory"))
        kwargs.setdefault(
            "help_text",
            _("Můžete přiložit více souborů najednou. Maximálně %(number)s souborů, každý nejvýše %(maxsize)s MB.") % {
                "number": settings.MAX_UPLOAD_FILES_NUMBER,
                "maxsize": settings.MAX_UPLOAD_FILE_SIZE_MB,
            }
        )
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
                _("Najednou můžeš nahrát maximálně %(mf)s souborů.")%{"mf":max_files}
            )

        for f in files:
            if f.size > max_size:
                raise ValidationError(
                    _("Soubor %(file)s je příliš velký. Maximum je %(msm)s MB.")%{"file":str(f),"msm":f"{max_size_mb:.0f}"}
                )
        return files

#vytvoření úkolu
class CreateHomeworkForm(forms.ModelForm):
    filesimput = MultipleFileField(
        help_text=_("Můžete přiložit více souborů najednou. Maximálně %(number)s souborů, každý nejvýše %(maxsize)s MB.") % {
    "number": settings.MAX_UPLOAD_FILES_NUMBER,
    "maxsize": settings.MAX_UPLOAD_FILE_SIZE_MB,
},
        required=False,
        label=_("Přiložit soubory")
    )
    def __init__(self, *args, **kwargs):
        self.assignment = kwargs.pop("assignment", None)
        super().__init__(*args, **kwargs)
    def clean(self):
        cleaned_data = super().clean()
        if self.assignment and timezone.now() > self.assignment.deadline:
            raise ValidationError(_("Nemůžeš odevzdat úkol po termínu odevzdání!"))
        return cleaned_data

    class Meta:
        model = Homework
        fields = ("programming_language", "engrossment")
        widgets = {
            "engrossment": CodeMirrorWidget()
        }

# úprava úkolu  
class HomeworkForm(forms.ModelForm):
    filesimput= MultipleFileField(help_text=_("Můžete přiložit více souborů najednou. Maximálně %(number)s souborů, každý nejvýše %(maxsize)s MB.") % {
    "number": settings.MAX_UPLOAD_FILES_NUMBER,
    "maxsize": settings.MAX_UPLOAD_FILE_SIZE_MB,
} ,required=False, label=_("Přiložit soubory"))
    
    def clean(self):
        cleaned_data = super().clean()
        deadline = self.instance.key.assignment.deadline

        if timezone.now() > deadline:
            raise ValidationError(_("Nemůžeš odevzdat úkol po termínu odevzdání!"))

        new_files = cleaned_data.get("filesimput", [])
        current_files_count = self.instance.total_files() if self.instance.pk else 0
        #nepřerkočit max nahraných souborů
        if current_files_count + len(new_files) > settings.MAX_UPLOAD_FILES_NUMBER:
            raise ValidationError(_(
                "Celkem může být u zadání maximálně %(mnf)s souborů.")%{"mnf":settings.MAX_UPLOAD_FILES_NUMBER})
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
    filesimput= MultipleFileField(help_text=_("Můžete přiložit více souborů najednou. Maximálně %(number)s souborů, každý nejvýše %(maxsize)s MB.") % {
    "number": settings.MAX_UPLOAD_FILES_NUMBER,
    "maxsize": settings.MAX_UPLOAD_FILE_SIZE_MB,} ,required=False, label=_("Přiložit soubory"))
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(AssignmentForm, self).__init__(*args, **kwargs)
        if self.user:
            self.fields["subject"].queryset = self.user.teacher_subjects
            self.fields["description"].help_text = format_html( _("Podporuje <a href='{url}' target='_blank'>Markdown syntaxi</a>."),url="https://www.daringfireball.net/projects/markdown/syntax",)
        
        
    def clean_subject(self):
        subject = self.cleaned_data["subject"]
        if self.user and not subject.subject_type.filter(user=self.user, role="teacher").exists():
            raise forms.ValidationError(_("Na tomto předmětu nejsi veden jako učitel."))
        return subject
    def clean(self):
        cleaned_data = super().clean()
        new_files = cleaned_data.get("filesimput", [])

        if len(new_files) > settings.MAX_UPLOAD_FILES_NUMBER:
            raise ValidationError(
               _("Můžeš přiložit maximálně %(mnf)s souborů.")%{"mnf":settings.MAX_UPLOAD_FILES_NUMBER}
            )

        return cleaned_data

    class Meta:
        model = Assignment
        fields = ("title", "subject", "description", "release", "deadline", "max_score")
        widgets = {
            "deadline": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "release": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
        
class AssignemntEdit(forms.ModelForm):
    filesimput= MultipleFileField(help_text=_("Můžete přiložit více souborů najednou. Maximálně %(number)s souborů, každý nejvýše %(maxsize)s MB.") % {
    "number": settings.MAX_UPLOAD_FILES_NUMBER,
    "maxsize": settings.MAX_UPLOAD_FILE_SIZE_MB,
} ,required=False, label=_("Přiložit soubory"))
    def __init__(self, *args, **kwargs):
        super(AssignemntEdit, self).__init__(*args, **kwargs)
        self.fields["description"].help_text = format_html( _("Podporuje <a href='{url}' target='_blank'>Markdown syntaxi</a>."),url="https://www.daringfireball.net/projects/markdown/syntax",)        
    def clean(self):
        cleaned_data = super().clean()
        new_files = cleaned_data.get("filesimput", [])
        current_files_count = self.instance.total_files() if self.instance.pk else 0
        #nepřerkočit max nahraných souborů
        if current_files_count + len(new_files) > settings.MAX_UPLOAD_FILES_NUMBER:
            raise ValidationError(_(
                "Celkem může být u odevzdání maximálně %(mnf)s souborů.")%{"mnf":settings.MAX_UPLOAD_FILES_NUMBER})
        release=self.instance.release
        if timezone.now() > release:
            raise ValidationError(_("Nelze editovat zadání, jestliže je již aktivní."))
        return cleaned_data
    class Meta:
        model=Assignment
        fields=("title","description","release","deadline", "max_score")        

#vyplnění hodnocení od učitele
class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = ["score","text_evaluation", ]
                
    def clean_score(self):
        score = self.cleaned_data.get("score")
        maxscore = self.instance.key.assignment.max_score
        
        if score is not None and score > maxscore:
            raise ValidationError(_("max score je %(maxscore)s")%{"maxscore":maxscore})
        return score
    
    # aby mohl učitel zadat maximálně max_score bodů
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['score'].widget.attrs.update({
            'min': 0,
            'max': self.instance.key.assignment.max_score, 

        })
        self.fields["score"].help_text = (_("Maximální počet bodů je %(mb)s")%{"mb":self.instance.key.assignment.max_score})
        self.fields["text_evaluation"].help_text = format_html( _("Podporuje <a href='{url}' target='_blank'>Markdown syntaxi</a>."),url="https://www.daringfireball.net/projects/markdown/syntax",)
    
# pro vyplnění komentu
class HomeworkStudentCommentForm(forms.ModelForm):
    class Meta:
        model=HomeworkStudentComment
        fields=("comment",)
        widgets = {
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 6, "placeholder": _("Napiš zpětnou vazbu...")}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["comment"].help_text = format_html( _("Podporuje <a href='{url}' target='_blank'>Markdown syntaxi</a>."),url="https://www.daringfireball.net/projects/markdown/syntax",)
    

# generování k-tic hodnotících k úkolu
class MakeCommentsForm(forms.Form):
    k=forms.IntegerField(min_value=1)
