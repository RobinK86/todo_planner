from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'title',
            'category',
            'description',
            'due_date',
            'recurrence',
            'completed',
            'location',
            'is_bill',
            'class_name',
            'assignment_type',
            'project_name',
            'meeting_required',
        ]
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }