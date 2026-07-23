from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django import forms
from django.utils.translation import gettext_lazy as _

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = (
            "username",
            "email",
            "first_name",
            "surname",
            "tel"
        )
        help_texts = {
            "username": _("Zadejte své uživatelské jméno."),
            "email": _("Zadejte svůj e-mail."),
            "first_name": _("Zadejte své křestní jméno."),
            "surname": _("Zadejte své příjmení."),
            "tel": _("Zadejte telefonní číslo."),
        }



class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "first_name",
            "surname",
            "tel"
        )
        help_texts = {
            "username": _("Zadejte své uživatelské jméno."),
            "email": _("Zadejte svůj e-mail."),
            "first_name": _("Zadejte své křestní jméno."),
            "surname": _("Zadejte své příjmení."),
            "tel": _("Zadejte telefonní číslo."),
        }
        

class EmailChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('email',)
        labels = {"email": _("E-mail")}
        help_texts = {"email": _("Zadejte nový e-mail.")}
        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "autocomplete": "email",
                    "placeholder": _("napriklad@example.com"),
                }
            ),
        }


class TelChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('tel',)
        labels = {"tel": _("Telefon")}
        help_texts = {"tel": _("Zadejte nové telefonní číslo.")}

        widgets = {
            "tel": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "autocomplete": "tel",
                    "placeholder": _("Například +420 123 456 789"),
                }
            ),
        }