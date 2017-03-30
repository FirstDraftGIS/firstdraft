from appfd.models import Basemap, Place
from apifd.serializers import BasemapSerializer, PlaceSerializer
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework.viewsets import ModelViewSet

# ViewSets define the view behavior.
class BasemapViewSet(ModelViewSet):
    queryset = Basemap.objects.all()
    serializer_class = BasemapSerializer

# ViewSets define the view behavior.
class PlaceViewSet(ModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    filter_fields = ('id','name')

    @list_route(methods=['get'])
    def typeahead(self, request):
        return Response(Place.objects.filter(name__startswith=request.query_params['name']).distinct("name").values_list("name", flat=True)[:5])

