from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib.auth.models import User, Group
from django.contrib.gis import admin
from django.conf import settings
import appfd, inspect
from . import views

urlpatterns = [
    url(r'^frequency/(?P<token>[^/]+)/(?P<admin_level>[^/]+)$', views.frequency, name='frequency'),
    url(r'^data$', views.data, name='data')
]
