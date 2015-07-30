from django.http import JsonResponse
from django.shortcuts import render

from appy.models import Application

def home(request):
    return render(request, 'home.html')

def list_applications(request):
    apps = Application.objects.all()
    return render(request, 'list.html', {'apps': apps})

def create_application(request):
    company = request.POST.get('company', '')
    position = request.POST.get('position', '')
    status = request.POST.get('status', '')
    link = request.POST.get('link', '')

    try:
        app = Application(
            company=company,
            position=position,
            status=status,
            link=link,
        )
        app.save()

        return JsonResponse({'success': True})
    except Exception:
        return JsonResponse({'success': False})