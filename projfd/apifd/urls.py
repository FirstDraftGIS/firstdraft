from appfd.models import Basemap
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib.auth.models import User, Group
from django.contrib.gis import admin
from django.conf import settings
import appfd, inspect
from . import views
from rest_framework import routers, serializers, viewsets

# Serializers define the API representation.
class BasemapSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Basemap
        fields = ["id", "name"]

# ViewSets define the view behavior.
class BasemapViewSet(viewsets.ModelViewSet):
    queryset = Basemap.objects.all()
    serializer_class = BasemapSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'basemaps', BasemapViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^frequency/(?P<token>[^/]+)/(?P<admin_level>[^/]+)$', views.frequency, name='frequency'),
    url(r'^data$', views.data, name='data'),
    url(r'^change_basemap$', views.change_basemap, name="change_basemap"),
    url(r'^change_featureplace$', views.change_featureplace, name="change_featureplace"),
    url(r'^is_location_in_osm$', views.is_location_in_osm, name='is_location_in_osm'),
    url(r'^features/(?P<token>[^/]+)$', views.features, name='features'),
    url(r'^metadata/(?P<token>[^/]+)$', views.metadata, name='metadata'),
    url(r'^ready/(?P<token>[^/]+)$', views.ready, name='ready')
]
