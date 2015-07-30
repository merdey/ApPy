from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^$', 'appy.views.home', name='home'),
    url(r'^applications/list$', 'appy.views.list_applications', name='list-applications'),
    url(r'^applications/create$', 'appy.views.create_application', name='create-application'),

    url(r'^admin/', include(admin.site.urls)),
]
