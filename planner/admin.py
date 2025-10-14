"""
Admin configuration for FocusFlow's core models.

Why this matters:
- Able to quickly browse and verify data relationships in /admin
- Adds list columns, filters, and search for a smoother review/demo
"""

from django.contrib import admin
from .models import Subject, Topic, Task, Session


# Register "Subject" with a compact, useful list view.
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    # Columns to display in the list page.
    list_display = ("name", "color", "user")
    # Quick search over subject names (case-insensitive).
    search_fields = ("name",)


# Register "Topic" with filters for status/subject so you can slice fast.
@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "status", "struggle_level", "user")
    # Sidebar filters to narrow results.
    list_filter = ("status", "subject")
    # Optional: enable searching by title if you want.
    search_fields = ("title",)


# Register "Task" with the fields reviewers typically want to see.
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "topic", "priority", "status", "due_date", "user")
    list_filter = ("priority", "status", "due_date")
    search_fields = ("title",)
    # Optional: default ordering (newest due first, then priority desc)
    ordering = ("due_date", "-priority")


# Register "Session" emphasizing timing and computed minutes.
@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("task", "started_at", "ended_at", "minutes", "user")
    list_filter = ("task", "started_at", "ended_at")
    # Readonly fields are often useful if minutes is computed server-side.
    readonly_fields = ("minutes",)

    # Optional: show newest sessions first
    ordering = ("-started_at",)


