from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib.auth.models import User, Group
from django.contrib.gis import admin
from django.conf import settings
import appfd, inspect
from . import views

urlpatterns = [
    url(r'^api$', views.api, name='api')
]
