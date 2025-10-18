from django.contrib import admin
from .models import Subject, Assignment, Key, Homework


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "year"]
    list_filter = ["year"]


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ["title", "subject", "teacher", "deadline", "release"]
    list_filter = ["subject", "teacher"]
    search_fields = ["title", "description"]


@admin.register(Key)
class KeyAdmin(admin.ModelAdmin):
    list_display = ["student", "assignment"]
    list_filter = ["assignment__subject"]
    autocomplete_fields = ["student", "assignment"]


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ["key", "submitted", "score"]
    list_filter = ["score"]
    search_fields = ["key__assignment__title", "key__student__username"]
