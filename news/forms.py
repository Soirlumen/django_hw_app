from django import forms
from .models import NewsPost
from django.utils.translation import gettext_lazy as _


class CreateEditPost(forms.ModelForm):
    class Meta:
        model = NewsPost
        fields = ("announcement",)
        help_texts = {
            "announcement": _("Zadejte text svého oznámení")
        }
    