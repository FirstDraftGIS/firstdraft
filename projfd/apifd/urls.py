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
    url(r'^delete_feature/(?P<feature_id>[^/]+)$', views.mark_feature_incorrect, name="mark_feature_incorrect"),
    url(r'^features/(?P<token>[^/]+)$', views.features, name='features'),
    url(r'^ready/(?P<token>[^/]+)$', views.ready, name='ready')
]
