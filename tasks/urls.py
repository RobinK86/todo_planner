from django.urls import path
from .views import (
    home,
    add_task,
    edit_task,
    delete_task,
    toggle_complete,
    toggle_checklist_item,
)

urlpatterns = [
    path('', home, name='home'),
    path('add/', add_task, name='add_task'),
    path('edit/<int:task_id>/', edit_task, name='edit_task'),
    path('delete/<int:task_id>/', delete_task, name='delete_task'),
    path('toggle/<int:task_id>/', toggle_complete, name='toggle_complete'),
    path('toggle-checklist/<int:item_id>/', toggle_checklist_item, name='toggle_checklist_item'),
]