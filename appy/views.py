from django.shortcuts import render

from appy.models import Application

def home(request):
    return render(request, 'home.html')

def list_applications(request):
    apps = Application.objects.all()
    return render(request, 'list.html', {'apps': apps})

def create_application(request):
    pass