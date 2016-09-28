from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib.auth.models import User, Group
from django.contrib.gis import admin
from django.conf import settings
import appfd, inspect
from . import views

urlpatterns = [
    url(r'^frequency/(?P<token>[^/]+)/(?P<admin_level>[^/]+)$', views.frequency, name='frequency'),
    url(r'^data$', views.data, name='data'),
    url(r'^change_featureplace$', views.change_featureplace, name="change_featureplace"),
    url(r'^features/(?P<token>[^/]+)$', views.features, name='features'),
    url(r'^ready/(?P<token>[^/]+)$', views.ready, name='ready')
]
