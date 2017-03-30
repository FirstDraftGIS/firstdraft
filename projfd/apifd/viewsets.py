from appfd.models import Basemap, Place
from apifd.serializers import BasemapSerializer, PlaceSerializer
from rest_framework.viewsets import ModelViewSet

# ViewSets define the view behavior.
class BasemapViewSet(ModelViewSet):
    queryset = Basemap.objects.all()
    serializer_class = BasemapSerializer

# ViewSets define the view behavior.
class PlaceViewSet(ModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
