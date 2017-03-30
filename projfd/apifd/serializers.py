from appfd.models import Basemap, Place
from rest_framework.serializers import HyperlinkedModelSerializer

# Serializers define the API representation.
class BasemapSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Basemap
        fields = ["id", "name"]

class PlaceSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Place
        fields = ["id", "country_code", "name", "point"]
