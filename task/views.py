from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Task, Note
from datetime import datetime, timedelta
import json

# Mock AI summary function (can be replaced with actual OpenAI integration)
def generate_ai_summary(tasks, period="week"):
    completed_tasks = [task for task in tasks if task.completed]
    pending_tasks = [task for task in tasks if not task.completed]
    overdue_tasks = [task for task in pending_tasks if task.is_overdue]
    
    # Calculate basic statistics
    completion_rate = len(completed_tasks) / len(tasks) * 100 if tasks else 0
    
    # Generate summary text
    summary = {
        "stats": {
            "total_tasks": len(tasks),
            "completed_tasks": len(completed_tasks),
            "pending_tasks": len(pending_tasks),
            "overdue_tasks": len(overdue_tasks),
            "completion_rate": round(completion_rate, 1)
        },
        "insights": [
            f"You've completed {len(completed_tasks)} tasks this {period}.",
            f"Your task completion rate is {round(completion_rate, 1)}%."
        ],
        "recommendations": []
    }
    
    # Add conditional insights and recommendations
    if len(overdue_tasks) > 0:
        summary["insights"].append(f"You have {len(overdue_tasks)} overdue tasks that need attention.")
        summary["recommendations"].append("Consider prioritizing your overdue tasks first.")
    
    if completion_rate < 50:
        summary["recommendations"].append("Your completion rate is below 50%. Try breaking down large tasks into smaller ones.")
    elif completion_rate > 80:
        summary["insights"].append("Great job maintaining a high completion rate!")
    
    if len(pending_tasks) > 10:
        summary["recommendations"].append("You have many pending tasks. Consider delegating or rescheduling some of them.")
    
    # Add a generic recommendation
    summary["recommendations"].append("Remember to take breaks and celebrate your accomplishments.")
    
    return summary

# Home view
def home(request):
    return render(request, 'task/home.html')

# Authentication views
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('task:task_list')
    else:
        form = UserCreationForm()
    return render(request, 'task/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('task:task_list')
    else:
        form = AuthenticationForm()
    return render(request, 'task/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('task:home')

# Task views
class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'task/task_list.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        queryset = Task.objects.filter(user=self.request.user).order_by('-created_at')
        
        # Apply filters if provided
        filter_option = self.request.GET.get('filter', '')
        
        if filter_option == 'pending':
            queryset = queryset.filter(completed=False)
        elif filter_option == 'completed':
            queryset = queryset.filter(completed=True)
        elif filter_option == 'today':
            today = timezone.now().date()
            queryset = queryset.filter(due_date__date=today)
        elif filter_option == 'week':
            today = timezone.now().date()
            week_later = today + timedelta(days=7)
            queryset = queryset.filter(due_date__date__range=[today, week_later])
        elif filter_option == 'overdue':
            today = timezone.now()
            queryset = queryset.filter(due_date__lt=today, completed=False)
        elif filter_option == 'high_priority':
            queryset = queryset.filter(priority='high')
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.request.GET.get('filter', '')
        return context

class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'task/task_detail.html'
    context_object_name = 'task'
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    template_name = 'task/task_form.html'
    fields = ['title', 'description', 'due_date', 'priority']
    success_url = reverse_lazy('task:task_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Task created successfully!')
        return super().form_valid(form)

class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    template_name = 'task/task_form.html'
    fields = ['title', 'description', 'due_date', 'priority', 'completed']
    success_url = reverse_lazy('task:task_list')
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Task updated successfully!')
        return super().form_valid(form)

class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    success_url = reverse_lazy('task:task_list')
    template_name = 'task/task_form.html'
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Task deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Note views
class NoteListView(LoginRequiredMixin, ListView):
    model = Note
    template_name = 'task/note_list.html'
    context_object_name = 'notes'
    
    def get_queryset(self):
        return Note.objects.filter(user=self.request.user).order_by('-created_at')

class NoteDetailView(LoginRequiredMixin, DetailView):
    model = Note
    template_name = 'task/note_detail.html'
    context_object_name = 'note'
    
    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)

class NoteCreateView(LoginRequiredMixin, CreateView):
    model = Note
    template_name = 'task/note_form.html'
    fields = ['title', 'content']
    success_url = reverse_lazy('task:note_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Note created successfully!')
        return super().form_valid(form)

class NoteUpdateView(LoginRequiredMixin, UpdateView):
    model = Note
    template_name = 'task/note_form.html'
    fields = ['title', 'content']
    success_url = reverse_lazy('task:note_list')
    
    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Note updated successfully!')
        return super().form_valid(form)

class NoteDeleteView(LoginRequiredMixin, DeleteView):
    model = Note
    success_url = reverse_lazy('task:note_list')
    template_name = 'task/note_form.html'
    
    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Note deleted successfully!')
        return super().delete(request, *args, **kwargs)

# AI Summary view
@login_required
def ai_summary_view(request):
    period = request.GET.get('period', 'week')
    
    # Get tasks based on period
    if period == 'week':
        start_date = timezone.now().date() - timedelta(days=7)
    elif period == 'month':
        start_date = timezone.now().date() - timedelta(days=30)
    elif period == 'year':
        start_date = timezone.now().date() - timedelta(days=365)
    else:  # all time
        start_date = None
    
    if start_date:
        tasks = Task.objects.filter(user=request.user, created_at__date__gte=start_date)
    else:
        tasks = Task.objects.filter(user=request.user)
    
    # Generate AI summary
    summary = generate_ai_summary(tasks, period)
    
    return render(request, 'task/ai_summary.html', {
        'summary': summary,
        'period': period
    })

# User profile view
@login_required
def profile_view(request):
    return render(request, 'task/profile.html')
