from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
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
        
