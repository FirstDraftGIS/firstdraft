from appfd.models import Basemap, Feature, Order, Place, Test
from drf_queryfields import QueryFieldsMixin
from rest_framework.serializers import HiddenField, IntegerField, NullBooleanField, CharField, ChoiceField, URLField
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer, Serializer, SerializerMethodField

####
from rest_framework.utils.serializer_helpers import (
    BindingDict, BoundField, JSONBoundField, NestedBoundField, ReturnDict,
    ReturnList
)

class MapRequestSerializer(Serializer):
    basemap = CharField(max_length=200, allow_blank=True, allow_null=True, required=False)
    case_insensitive = NullBooleanField(required=False)
    end_user_timezone = CharField(max_length=200, allow_null=True, required=False)
    map_format = ChoiceField(["all","geojson", "gif", "jpg", "png", "xy"], required=False)
    text = CharField(max_length=1e10, trim_whitespace=True, allow_null=True, required=False)
    url = URLField(allow_null=True, required=False)


# Serializers define the API representation.
class BasemapSerializer(QueryFieldsMixin, ModelSerializer):
    class Meta:
        model = Basemap
        fields = ["id", "name"]

class FeatureSerializer(QueryFieldsMixin, HyperlinkedModelSerializer):
    class Meta:
        model = Feature
        fields = ["name", "order"]

class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = ["complete", "duration", "end", "start", "token"]


class QueryableOrderSerializer(QueryFieldsMixin, OrderSerializer):
    class Meta:
        model = Order
        fields = ["complete", "duration", "end", "start", "token"]

class PlaceSerializer(QueryFieldsMixin, ModelSerializer):

    """
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
    """
    
    class Meta:
        model = Place
        fields = ["id", "attribution", "country_code", "name", "point"]

class VerbosePlaceSerializer(PlaceSerializer):
    class Meta:
        model = Place
        fields = [
            "id", "name",
            "attribution", "enwiki_title", "geonames_id", "osm_id",
            "pcode", "fips",
            "admin1_code", "admin2_code", "admin3_code", "admin4_code", "admin_level",
            "east", "north", "south", "west",
            "name", "name_ascii", "name_display", "name_en", "name_normalized", "other_names",
            "geonames_feature_class", "geonames_feature_code", "place_type",
            "latitude", "longitude", "area_sqkm",
            "importance", "osmname_class", "osmname_type", "osm_type", "place_rank",
            "dem", "elevation",
            "city", "county", "country", "country_code", "state", "street",
            "population", "popularity", "timezone"
        ]



class TestSerializer(QueryFieldsMixin, ModelSerializer):
    class Meta:
        model = Test
        fields = ["accuracy", "created"]
