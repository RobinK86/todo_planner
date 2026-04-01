from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    CATEGORY_CHOICES = [
        ('life', 'Real Life'),
        ('school', 'School'),
        ('work', 'Work'),
    ]

    RECURRENCE_CHOICES = [
        ('none', 'None'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)

    due_date = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    recurrence = models.CharField(
        max_length=10,
        choices=RECURRENCE_CHOICES,
        default='none'
    )

    location = models.CharField(max_length=200, blank=True)
    is_bill = models.BooleanField(default=False)

    class_name = models.CharField(max_length=100, blank=True)
    assignment_type = models.CharField(max_length=100, blank=True)

    project_name = models.CharField(max_length=100, blank=True)
    meeting_required = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class ChecklistItem(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='checklist_items')
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title