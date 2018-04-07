from appfd.models import Basemap
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib.auth.models import User, Group
from django.contrib.gis import admin
from django.conf import settings
import appfd, inspect
from . import views
from rest_framework import routers, serializers, viewsets
from apifd.viewsets import AIViewSet, BasemapViewSet, FeatureViewSet, OrderViewSet, PlaceViewSet, TestViewSet

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'ai', AIViewSet, base_name="ai")
router.register(r'basemaps', BasemapViewSet)
router.register(r'features', FeatureViewSet, "feature")
router.register(r'orders', OrderViewSet, "order")
router.register(r'places', PlaceViewSet)
router.register(r'tests', TestViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^geolocate_tweet$', views.geolocate_tweet, name="geolocate_tweet"),
    url(r'^frequency/(?P<token>[^/]+)/(?P<admin_level>[^/]+)$', views.frequency, name='frequency'),
    url(r'^data$', views.data, name='data'),
    url(r'^change_basemap$', views.change_basemap, name="change_basemap"),
    url(r'^change_featureplace$', views.change_featureplace, name="change_featureplace"),
    url(r'^is_location_in_osm$', views.is_location_in_osm, name='is_location_in_osm'),
    url(r'^feature_data/(?P<token>[^/]+)$', views.feature_data, name='feature_data'),
    url(r'^metadata/(?P<token>[^/]+)$', views.metadata, name='metadata'),
]
