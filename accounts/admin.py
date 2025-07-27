from django.contrib import admin
from hw.models import Subject
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, StudentProfile, TeacherProfile

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "department")
    filter_horizontal = ("subjects",)  # Použití filter_horizontal pro subjects
    autocomplete_fields = ['user']  # Pro lepší vyhledávání uživatelů

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user",)
    filter_horizontal= ("subjects",)
    autocomplete_fields = ['user']  # Pro lepší vyhledávání uživatelů

    def get_subjects(self, obj):
        return ", ".join([s.name for s in obj.subjects.all()])
    get_subjects.short_description = "Subjects"

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ["email", "username", "role", "is_staff"]
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email")
    ordering = ("email",)

    # Vytvoření uživatele
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "role", "password1", "password2"),
        }),
    )

    # Úprava uživatele
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("email",)}),
        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions"
            ),
        }),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        ("Role info", {"fields": ("role",)}),
    )

    def save_model(self, request, obj, form, change):
        """Automaticky vytvoří profil při vytvoření nového uživatele"""
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)
        
        if is_new:
            if obj.role == "student":
                StudentProfile.objects.get_or_create(user=obj)
            elif obj.role == "teacher":
                TeacherProfile.objects.get_or_create(user=obj)

# Registrace modelů
admin.site.register(CustomUser, CustomUserAdmin)