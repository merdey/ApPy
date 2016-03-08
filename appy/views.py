from collections import defaultdict

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from appy.models import Application, Position, Tag
from appy.utils import apply_for_position


def home(request):
    return render(request, 'home.html')


@require_POST
def signup(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    if username and password:
        user = User.objects.create_user(username=username, password=password)
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
        company = request.POST.get('company', None)
        job_title = request.POST.get('job_title', None)
        tag_search = request.POST.get('tag_search', None)
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


def search_positions(company, job_title, tag_search):
    positions = Position.objects.all()
    if company:
        positions = positions.filter(company__icontains=company)
    if job_title:
        positions = positions.filter(job_title__icontains=job_title)
    if tag_search:
        p_ids = set()
        tags = Tag.objects.filter(description__icontains=tag_search)
        for tag in tags:
            for p in tag.position_set.all():
                p_ids.add(p.id)
        positions = positions.filter(id__in=p_ids)

    return positions


def sort_positions(positions, user):
    user_tag_counts = defaultdict(int)
    for app in Application.objects.filter(user=user).prefetch_related('position__tags'):
        tags = app.position.tags.all()
        for t in tags:
            user_tag_counts[t.description] += 1

    return sorted(positions, key=lambda p: recommendation_score(p, user_tag_counts), reverse=True)

def recommendation_score(position, user_tag_counts):
    score = 0
    tags = position.tags.all()
    for t in tags:
        score += user_tag_counts[t.description]
    return score

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
