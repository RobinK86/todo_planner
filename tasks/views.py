from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Task, ChecklistItem
from .forms import TaskForm
import calendar
from datetime import date, timedelta


@login_required
def home(request):
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    selected_date = request.GET.get('date')
    view_mode = request.GET.get('view', 'month')

    tasks = Task.objects.filter(user=request.user)

    if selected_date:
        tasks = tasks.filter(due_date=selected_date)
        task_heading = f"Tasks for {selected_date}"
    elif view_mode == 'today':
        tasks = tasks.filter(due_date=today)
        task_heading = "Tasks for Today"
    elif view_mode == 'overdue':
        tasks = tasks.filter(due_date__lt=today, completed=False)
        task_heading = "Overdue Tasks"
    elif view_mode == 'upcoming':
        tasks = tasks.filter(due_date__gt=today, completed=False)
        task_heading = "Upcoming Tasks"
    elif view_mode == 'week':
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        tasks = tasks.filter(due_date__gte=week_start, due_date__lte=week_end)
        task_heading = f"This Week ({week_start.strftime('%b %d')} – {week_end.strftime('%b %d')})"
    else:
        tasks = tasks.filter(due_date__year=year, due_date__month=month)
        task_heading = f"Tasks for {calendar.month_name[month]} {year}"

    tasks = tasks.order_by('due_date', 'title')

    for task in tasks:
        task.total_checklist_items = task.checklist_items.count()
        task.completed_checklist_items = task.checklist_items.filter(completed=True).count()
        task.incomplete_items = task.checklist_items.filter(completed=False)
        task.complete_items = task.checklist_items.filter(completed=True)

        if task.total_checklist_items > 0:
            task.progress_percent = int(
                (task.completed_checklist_items / task.total_checklist_items) * 100
            )
            task.progress_bucket = round(task.progress_percent / 10) * 10
        else:
            task.progress_percent = 100 if task.completed else 0
            task.progress_bucket = task.progress_percent

        task.should_start_open = False

    month_tasks = Task.objects.filter(
        user=request.user,
        due_date__year=year,
        due_date__month=month
    )

    day_tasks = {}
    for task in month_tasks:
        if task.due_date:
            day_num = task.due_date.day
            if day_num not in day_tasks:
                day_tasks[day_num] = []
            day_tasks[day_num].append(task)

    cal = calendar.Calendar()
    raw_month_days = cal.monthdatescalendar(year, month)

    month_days = []
    for week in raw_month_days:
        week_data = []
        for day in week:
            tasks_for_day = day_tasks.get(day.day, []) if day.month == month else []

            categories = []
            for task in tasks_for_day:
                if task.category not in categories:
                    categories.append(task.category)

            day_string = day.strftime('%Y-%m-%d')
            is_selected = selected_date == day_string

            if is_selected:
                day_link = f'/?month={month}&year={year}'
            else:
                day_link = f'/?date={day_string}&month={month}&year={year}'

            week_data.append({
                'date': day,
                'day': day.day,
                'in_month': day.month == month,
                'is_today': day == today,
                'is_selected': is_selected,
                'task_count': len(tasks_for_day),
                'categories': categories[:3],
                'extra_count': max(0, len(tasks_for_day) - 3),
                'link': day_link,
            })
        month_days.append(week_data)

    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year

    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    context = {
        'tasks': tasks,
        'month_days': month_days,
        'current_month': calendar.month_name[month],
        'current_year': year,
        'current_month_number': month,
        'selected_date': selected_date,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'today': today,
        'task_heading': task_heading,
        'view_mode': view_mode,
    }

    return render(request, 'tasks/home.html', context)


@login_required
def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()

            checklist_items = request.POST.getlist('checklist_items')
            for item_title in checklist_items:
                item_title = item_title.strip()
                if item_title:
                    ChecklistItem.objects.create(task=task, title=item_title)

            return redirect('home')
    else:
        form = TaskForm()

    return render(request, 'tasks/add_task.html', {
        'form': form,
        'checklist_values': [''],
        'is_edit': False,
    })


@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()

            task.checklist_items.all().delete()

            checklist_items = request.POST.getlist('checklist_items')
            for item_title in checklist_items:
                item_title = item_title.strip()
                if item_title:
                    ChecklistItem.objects.create(task=task, title=item_title)

            return redirect('home')
    else:
        form = TaskForm(instance=task)
        existing_items = list(task.checklist_items.values_list('title', flat=True))
        checklist_values = existing_items if existing_items else ['']

    return render(request, 'tasks/add_task.html', {
        'form': form,
        'checklist_values': checklist_values,
        'is_edit': True,
        'task': task,
    })


@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    return redirect('home')


@login_required
def toggle_complete(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)

    checklist_items = task.checklist_items.all()

    if checklist_items.exists():
        all_done = all(item.completed for item in checklist_items)
        if not all_done:
            return redirect('home')

    if not task.completed:
        task.completed = True
        task.save()

        if task.recurrence != 'none' and task.due_date:
            if task.recurrence == 'daily':
                next_date = task.due_date + timedelta(days=1)
            elif task.recurrence == 'weekly':
                next_date = task.due_date + timedelta(weeks=1)
            elif task.recurrence == 'monthly':
                next_date = task.due_date + timedelta(days=30)
            else:
                next_date = None

            if next_date:
                Task.objects.create(
                    user=task.user,
                    title=task.title,
                    category=task.category,
                    description=task.description,
                    due_date=next_date,
                    recurrence=task.recurrence,
                    location=task.location,
                    is_bill=task.is_bill,
                    class_name=task.class_name,
                    assignment_type=task.assignment_type,
                    project_name=task.project_name,
                    meeting_required=task.meeting_required,
                )
    else:
        task.completed = False
        task.save()

    return redirect('home')


@login_required
def toggle_checklist_item(request, item_id):
    item = get_object_or_404(ChecklistItem, id=item_id, task__user=request.user)
    item.completed = not item.completed
    item.save()

    task = item.task
    checklist_items = task.checklist_items.all()

    all_done = checklist_items.exists() and all(i.completed for i in checklist_items)

    if all_done and not task.completed:
        task.completed = True
        task.save()

        if task.recurrence != 'none' and task.due_date:
            if task.recurrence == 'daily':
                next_date = task.due_date + timedelta(days=1)
            elif task.recurrence == 'weekly':
                next_date = task.due_date + timedelta(weeks=1)
            elif task.recurrence == 'monthly':
                next_date = task.due_date + timedelta(days=30)
            else:
                next_date = None

            if next_date:
                Task.objects.create(
                    user=task.user,
                    title=task.title,
                    category=task.category,
                    description=task.description,
                    due_date=next_date,
                    recurrence=task.recurrence,
                    location=task.location,
                    is_bill=task.is_bill,
                    class_name=task.class_name,
                    assignment_type=task.assignment_type,
                    project_name=task.project_name,
                    meeting_required=task.meeting_required,
                )
    elif not all_done:
        task.completed = False
        task.save()

    return redirect(f'/#task-{task.id}')