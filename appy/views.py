from collections import defaultdict

from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.http import require_POST

from appy.models import Application
from appy.models import Position
from appy.models import Reminder
from appy.models import Tag
from appy.utils import apply_for_position
from appy.utils import search_positions
from appy.utils import sort_positions


def home(request):
    return render(request, 'home.html')


@require_POST
def signup(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    if username and password:
        User.objects.create_user(username=username, password=password)
        user = authenticate(username=username, password=password)
        login(request, user)
        return redirect('positions')
    else:
        return render(request, 'home.html', {'errors': 'Unable to create user'})


@require_POST
def login_view(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    if username and password:
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('positions')

    return render(request, 'home.html', {'errors': 'Unable to log in'})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def positions(request):
    context = {}
    if request.method == 'POST':
        company = request.POST.get('company')
        job_title = request.POST.get('job_title')
        tag_search = request.POST.get('tag_search')
        context.update({'company': company, 'job_title': job_title, 'tag_search': tag_search})
        positions = search_positions(company, job_title, tag_search)
    else:
        positions = Position.objects.all()

    applied_to = set([app.position for app in Application.objects.filter(user=request.user)])
    for position in positions:
        position.already_applied = position in applied_to

    positions = sort_positions(positions, request.user)

    context.update({'positions': positions})
    return render(request, 'positions.html', context)


@login_required
def create_position(request):
    if request.method == 'POST':
        company = request.POST.get('company')
        job_title = request.POST.get('job_title')
        description = request.POST.get('description')

        tags = []
        tag_list = request.POST.get('tags')
        for tag_name in tag_list.split(','):
            tag_name = tag_name.strip()
            try:
                t = Tag.objects.get(description=tag_name)
            except Tag.DoesNotExist:
                t = Tag.objects.create(description=tag_name)
            tags.append(t)

        position = Position.objects.create(
            company=company,
            job_title=job_title,
            description=description
        )

        for t in tags:
            position.tags.add(t)

        return render(request, 'create_position.html')
    else:
        return render(request, 'create_position.html')


@login_required
@require_POST
def create_reminder(request):
    status = request.POST['reminder-status']
    duration = request.POST['reminder-duration']
    contact_method = request.POST['reminder-method']
    contact_info = request.POST['reminder-contact-info']

    if Reminder.is_valid_duration(duration):
        Reminder.objects.create(
            user=request.user,
            status=status,
            duration=duration,
            contact_method=contact_method,
            contact_info=contact_info,
        )

    return applications(request)


@login_required
def applications(request):
    applications = Application.objects.filter(user=request.user)
    status_choices = Application.STATUS_CHOICES
    reminders = Reminder.objects.filter(user=request.user)

    return render(request, 'applications.html', {
        'applications': applications,
        'status_choices': status_choices,
        'reminders': reminders,
    })


@login_required
def apply(request):
    user = request.user
    position_id = request.POST.get('position_id')
    position = Position.objects.get(id=position_id)

    apply_for_position(position, user)
    return JsonResponse({'success': True})


@login_required
def update_status(request):
    app_id = request.POST.get('app_id')
    new_status = request.POST.get('new_status')
    app = Application.objects.get(user=request.user, id=app_id)

    app.status = new_status
    app.save()
    return JsonResponse({'success': True})


@login_required
def delete_app(request):
    app_id = request.POST.get('app_id')
    app = Application.objects.get(user=request.user, id=app_id)

    app.delete()
    return JsonResponse({'success': True})
