from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.shortcuts import redirect, render

from appy.models import Application, Position


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
    positions = Position.objects.all()

    return render(request, 'positions.html', {
        'positions': positions,
    })


@login_required
def applications(request):
    user = request.user
    applications = Application.objects.filter(user=user)

    return render(request, 'applications.html', {
        'applications': applications,
    })
