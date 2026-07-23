from django import forms
from .models import Homework, Assignment, HomeworkStudentComment,Subject
from django.core.exceptions import ValidationError
from .validators import validate_file_type
from django.utils import timezone
from django.utils.html import format_html
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
                
        try:
            validate_file_type(f)
        except ValidationError as e:
            raise ValidationError(
                    _("Soubor %(file)s má nepovolený typ: %(err)s") % 
                    {"file": str(f), 
                        "err": e.message}
                )
        except Exception:
                raise ValidationError(
                    _("Soubor %(file)s nelze zpracovat nebo má neplatný formát.") % {"file": str(f)}
                )
        return files

class HomeworkBaseForm(forms.ModelForm):
    filesimput = MultipleFileField( required=False, label=_("Přiložit soubory"),
        help_text=_(
            "Můžete přiložit více souborů najednou. "
            "Maximálně %(number)s souborů, každý nejvýše %(maxsize)s MB.") % {"number": settings.MAX_UPLOAD_FILES_NUMBER,"maxsize": settings.MAX_UPLOAD_FILE_SIZE_MB,},
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["programming_language"].error_messages["invalid_choice"] = _("Neplatný programovací jazyk.")

    def validate_solution_presence( self, cleaned_data,final_file_count: int,) -> None:
        """Ověří, že odevzdání obsahuje text nebo alespoň jeden soubor."""
        engrossment = cleaned_data.get("engrossment") or ""
        if not engrossment.strip() and final_file_count == 0:
            raise ValidationError(
                _("Vyplňte text řešení nebo přiložte alespoň jeden soubor.")
            )

    class Meta:
        model = Homework
        fields = ("programming_language","engrossment","notes",)
        widgets = {
            "engrossment": CodeMirrorWidget(attrs={"maxlength": str(settings.MAX_HOMEWORK_LENGTH)}
            ),
            "notes": forms.Textarea(
                attrs={"maxlength": str(settings.MAX_HOMEWORK_LENGTH),"rows": 5,}
            ),
        }

#vytvoření úkolu
class CreateHomeworkForm(HomeworkBaseForm):
    def __init__(self, *args, **kwargs):
        self.assignment = kwargs.pop("assignment", None)
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if self.assignment is None:
            raise ValidationError(
                _("Chybí zadání, ke kterému má být řešení odevzdáno.")
            )
        if self.user is None:
            raise ValidationError(
                _("Chybí autor odevzdávaného řešení.")
            )
        now = timezone.now()
        if now < self.assignment.release:
            raise ValidationError(
                _("Zadání ještě nebylo zveřejněno.")
            )
        if now >= self.assignment.deadline:
            raise ValidationError(
                _("Úkol již nelze odevzdat, protože vypršel termín.")
            )

        new_files = cleaned_data.get("filesimput") or []
        # zkontrolujeme přítomnost textu nebo souboru.
        if "filesimput" not in self.errors:
            self.validate_solution_presence( cleaned_data, final_file_count=len(new_files))
        return cleaned_data
    
# úprava úkolu  
class HomeworkForm(HomeworkBaseForm):
    def clean(self):
        cleaned_data = super().clean()
        if not self.instance.pk:
            raise ValidationError(
                _("Nelze upravit neexistující odevzdání.")
            )
        deadline = self.instance.key.assignment.deadline
        if timezone.now() >= deadline:
            raise ValidationError(
                _("Úkol již nelze upravit, protože vypršel termín.")
            )
        new_files = cleaned_data.get("filesimput") or []
        requested_removed_ids = self.data.getlist("remove_files")
        current_files = self.instance.files.all()

        # Započítají se pouze soubory, které opravdu patří k upravovanému odevzdání
        removed_files_count = current_files.filter( pk__in=requested_removed_ids).count()
        remaining_files_count = ( current_files.count() - removed_files_count)
        final_file_count = remaining_files_count + len(new_files)
        if final_file_count > settings.MAX_UPLOAD_FILES_NUMBER:
            self.add_error(
                "filesimput",
                _("Celkem může být k odevzdání přiloženo maximálně %(max_count)s souborů.") % {
                    "max_count": settings.MAX_UPLOAD_FILES_NUMBER,
                },
            )
        if "filesimput" not in self.errors:
            self.validate_solution_presence(cleaned_data, final_file_count=final_file_count)
        return cleaned_data
    
#vytvoření zadání úkolu
class AssignmentForm(forms.ModelForm):
    max_size=settings.MAX_UPLOAD_FILE_SIZE/(1024**2)
    filesimput= MultipleFileField(help_text=_("Můžete přiložit více souborů najednou. Maximálně %(number)s souborů, každý nejvýše %(maxsize)s MB.") % {
    "number": settings.MAX_UPLOAD_FILES_NUMBER,
    "maxsize": settings.MAX_UPLOAD_FILE_SIZE_MB,} ,required=False, label=_("Přiložit soubory"))
    release = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"},format="%Y-%m-%dT%H:%M"),)
    deadline = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"},format="%Y-%m-%dT%H:%M"),)
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(AssignmentForm, self).__init__(*args, **kwargs)
        if self.user:
            self.fields["subject"].queryset = self.user.teacher_subjects
            self.fields["description"].help_text = format_html( _("Podporuje <a href='{url}' target='_blank'>Markdown syntaxi</a>."),url="https://www.daringfireball.net/projects/markdown/syntax",)
            self.fields["subject"].error_messages['invalid_choice'] = _("Na tomto předmětu nejsi veden jako učitel.")

    def clean(self):
        cleaned_data = super().clean()
        release = cleaned_data.get("release")
        deadline = cleaned_data.get("deadline")
        new_files = cleaned_data.get("filesimput", [])
        if release and deadline and deadline < release:
            self.add_error("release", _("Termín odevzdání nemůže být dříve než zveřejnění."))

        if len(new_files) > settings.MAX_UPLOAD_FILES_NUMBER:
            self.add_error("filesimput", _("Můžeš přiložit maximálně %(mnf)s souborů.") % {"mnf": settings.MAX_UPLOAD_FILES_NUMBER})

        if not self.user:
            raise ValidationError(_("Chybí autor zadání."))

        return cleaned_data

    class Meta:
        model = Assignment
        fields = ("title", "subject", "description", "release", "deadline", "max_score")
        widgets = {
            "description": forms.Textarea(attrs={'maxlength': settings.MAX_HOMEWORK_LENGTH}),
            }
        
class AssignemntEdit(forms.ModelForm):
    filesimput= MultipleFileField(help_text=_("Můžete přiložit více souborů najednou. Maximálně %(number)s souborů, každý nejvýše %(maxsize)s MB.") % {
    "number": settings.MAX_UPLOAD_FILES_NUMBER,
    "maxsize": settings.MAX_UPLOAD_FILE_SIZE_MB,
} ,required=False, label=_("Přiložit soubory"))
    release = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"},format="%Y-%m-%dT%H:%M"),)
    deadline = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"},format="%Y-%m-%dT%H:%M"),)
    def __init__(self, *args, **kwargs):
        super(AssignemntEdit, self).__init__(*args, **kwargs)
        self.fields["description"].help_text = format_html( _("Podporuje <a href='{url}' target='_blank'>Markdown syntaxi</a>."),url="https://www.daringfireball.net/projects/markdown/syntax",)        
    def clean(self):
        cleaned_data = super().clean()
        original_release = self.instance.release
        new_release = cleaned_data.get("release")
        now = timezone.now()
        #nepřerkočit max nahraných souborů
        new_files = cleaned_data.get("filesimput",[])
        requested_removed_ids = self.data.getlist("remove_files")
        current_files = self.instance.files.all()

        removed_files_count = current_files.filter( pk__in=requested_removed_ids).count()
        remaining_files_count = ( current_files.count() - removed_files_count)
        final_file_count = remaining_files_count + len(new_files)
        if final_file_count > settings.MAX_UPLOAD_FILES_NUMBER:
            self.add_error(
                "filesimput",
                _("Celkem může být k odevzdání přiloženo maximálně %(max_count)s souborů.") % {
                    "max_count": settings.MAX_UPLOAD_FILES_NUMBER,
                },
            )
        if original_release <= now:
            raise ValidationError(
                _("Již zveřejněné zadání nelze upravovat.")
        )

        if new_release and new_release <= now:
            self.add_error(
                "release",
                _("Nový čas zveřejnění musí být v budoucnosti.")
            )
    class Meta:
        model=Assignment
        fields=("title","description","release","deadline", "max_score")
        widgets = {
            "description": forms.Textarea(attrs={'maxlength': settings.MAX_HOMEWORK_LENGTH}),
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
            "comment": forms.Textarea(attrs={"class": "form-control", 
                                             "rows": 6, 
                                             "placeholder": _("Napiš zpětnou vazbu..."),
                                             "maxlength":settings.MAX_HOMEWORK_LENGTH}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["comment"].help_text = format_html( _("Podporuje <a href='{url}' target='_blank'>Markdown syntaxi</a>."),url="https://www.daringfireball.net/projects/markdown/syntax",)
    

# generování k-tic hodnotících k úkolu
class MakeCommentsForm(forms.Form):
    k=forms.IntegerField(min_value=1)
    
class CommentTeacherMarkForm(forms.ModelForm):
    class Meta:
        model=HomeworkStudentComment
        fields=["mark"]
        
class SubjectCreateForm(forms.ModelForm):
    class Meta:
        model=Subject
        fields=["year","name"]