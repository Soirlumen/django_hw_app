from django.contrib import admin
from hw.models import Subject
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, SubjectType

class SubjectTypeInline(admin.TabularInline):
    model = SubjectType
    extra = 1
    autocomplete_fields = ["subject"] 

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    inlines = [SubjectTypeInline]

    list_display = (
        "username",
        "email",
        "is_staff",
        "student_subjects_count",
        "teacher_subjects_count",
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
    )
    search_fields = ("username", "email", "first_name", "surname")
    ordering = ("username",)

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "first_name","surname","tel","email", "password1", "password2"),
            },
        ),
    )

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("email","first_name","surname","tel")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    def student_subjects_count(self, obj):
        return obj.subject_type.filter(role="student").count()
    student_subjects_count.short_description = "Předmětů (student)"

    def teacher_subjects_count(self, obj):
        return obj.subject_type.filter(role="teacher").count()
    teacher_subjects_count.short_description = "Předmětů (učitel)"

@admin.register(SubjectType)
class SubjectTypeAdmin(admin.ModelAdmin):
    list_display = ("user", "subject", "role")
    list_filter = ("role",)
    search_fields = ("user__username", "user__email", "subject__name")
    autocomplete_fields = ("user", "subject")

admin.site.register(CustomUser, CustomUserAdmin)

