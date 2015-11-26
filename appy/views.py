from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.http import JsonResponse
from django.shortcuts import redirect, render

from appy.models import Application, Position, Tag
from appy.utils import apply_for_position


def home(request):
    return render(request, 'home.html')


def signup(request):
    context = {}
    context.update(csrf(request))
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = User.objects.create_user(username=username, password=password)

        return render(request, 'home.html')
    else:
        return render(request, 'login.html', context)


def login_view(request):
    context = {}
    context.update(csrf(request))
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('positions')
        else:
            context['errors'] = 'Username or password was incorrect'
            return render(request, 'login.html', context)
    else:
        return render(request, 'login.html', context)


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def positions(request):
    if request.method == 'POST':
        positions = search_positions(request)
    else:
        positions = Position.objects.all()

    applied_to = set([app.position for app in Application.objects.filter(user=request.user)])

    for position in positions:
        position.already_applied = position in applied_to

    return render(request, 'positions.html', {
        'positions': positions,
    })


def search_positions(request):
    company = request.POST.get('company', None)
    title = request.POST.get('title', None)
    tag_search = request.POST.get('tag_search', None)

    positions = Position.objects.all()
    if company:
        positions = positions.filter(company__icontains=company)
    if title:
        positions = positions.filter(job_title__icontains=title)
    if tag_search:
        p_ids = set()
        tags = Tag.objects.filter(description__icontains=tag_search)
        for tag in tags:
            for p in tag.position_set.all():
                p_ids.add(p.id)
        positions = positions.filter(id__in=p_ids)

    return positions


@login_required
def applications(request):
    applications = Application.objects.filter(user=request.user)
    status_choices = Application.STATUS_CHOICES

    return render(request, 'applications.html', {
        'applications': applications,
        'status_choices': status_choices,
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
