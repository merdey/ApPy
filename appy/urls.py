from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^$', 'appy.views.home', name='home'),

    url(r'^signup$', 'appy.views.signup', name='signup'),
    url(r'^login$', 'appy.views.login_view', name='login'),
    url(r'^logout$', 'appy.views.logout_view', name='logout'),

    url(r'^positions$', 'appy.views.positions', name='positions'),

    url(r'^admin/', include(admin.site.urls)),
]
