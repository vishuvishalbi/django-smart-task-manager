from django.contrib import admin
from .models import Task, Note

# Register Task model with custom display
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'due_date', 'priority', 'completed', 'is_overdue')
    list_filter = ('completed', 'priority', 'created_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'

# Register Note model
@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'content')
