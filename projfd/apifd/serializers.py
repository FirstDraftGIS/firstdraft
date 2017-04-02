from appfd.models import Basemap, Feature, Order, Place
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
            "PPL": "Populated Place",
            "PPLA": "Admin 1",
            "PPLL": "Populated Locality",
            "ST": "Street"
        }
        return lookup.get(place.feature_code, place.feature_code)

    class Meta:
        model = Place
        fields = ["id", "admin_level", "country_code", "feature_code", "feature_type", "name", "point", "population"]
