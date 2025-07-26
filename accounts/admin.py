from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, StudentProfile, TeacherProfile

# --- Inline profily ---

class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = "Student profile"
    fk_name = "user"

class TeacherProfileInline(admin.StackedInline):
    model = TeacherProfile
    can_delete = False
    verbose_name_plural = "Teacher profile"
    fk_name = "user"

# --- Vlastní admin pro uživatele ---

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ["email", "username", "role", "is_staff"]
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("role",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("role",)}),)

    # Dynamické přidání inline podle role
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        inlines = []
        if obj.role == "student":
            inlines.append(StudentProfileInline(self.model, self.admin_site))
        elif obj.role == "teacher":
            inlines.append(TeacherProfileInline(self.model, self.admin_site))
        return inlines

# --- Registrace ---
admin.site.register(CustomUser, CustomUserAdmin)
