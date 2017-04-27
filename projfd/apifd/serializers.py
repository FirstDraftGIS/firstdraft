from appfd.models import Basemap, Feature, Order, Place, Test
from drf_queryfields import QueryFieldsMixin
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer, SerializerMethodField

# Serializers define the API representation.
class BasemapSerializer(QueryFieldsMixin, ModelSerializer):
    class Meta:
        model = Basemap
        fields = ["id", "name"]

class FeatureSerializer(QueryFieldsMixin, HyperlinkedModelSerializer):
    class Meta:
        model = Feature
        fields = ["name", "order"]

class OrderSerializer(QueryFieldsMixin, ModelSerializer):
    class Meta:
        model = Order
        fields = ["complete", "duration", "end", "start", "token"]


class PlaceSerializer(QueryFieldsMixin, ModelSerializer):

    feature_type = SerializerMethodField()

    def get_feature_type(self, place):
        lookup = {
            "FRM": "Farm",
            "PCLI": "Independent Political Entity",
            "PPL": "Populated Place",
            "PPLA": "Admin 1",
            "PPLA2": "Admin 2",
            "PPLA3": "Admin 3",
            "PPLA4": "Admin 4",
            "PPLL": "Populated Locality",
            "ST": "Street"
        }
        return lookup.get(place.feature_code, place.feature_code)

    class Meta:
        model = Place
        fields = ["id", "admin_level", "country_code", "feature_code", "feature_type", "name", "point", "population"]

class VerbosePlaceSerializer(PlaceSerializer):
    class Meta:
        model = Place
        fields = ["id", "admin_level", "country_code", "feature_code", "feature_type", "geonameid", "name", "point", "population"]



class TestSerializer(QueryFieldsMixin, ModelSerializer):
    class Meta:
        model = Test
        fields = ["accuracy", "created"]
