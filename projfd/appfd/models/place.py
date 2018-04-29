#-*- coding: utf-8 -*-
from .base import Base
from django.contrib.gis.db.models import BigIntegerField
from django.contrib.gis.db.models import TextField
from django.contrib.gis.db.models import FloatField
from django.contrib.gis.db.models import ForeignKey
from django.contrib.gis.db.models import IntegerField
from django.contrib.gis.db.models import Manager as GeoManager
from django.contrib.gis.db.models import MultiLineStringField
from django.contrib.gis.db.models import MultiPolygonField
from django.contrib.gis.db.models import PointField
from django.contrib.gis.db.models import SET_NULL
from django.contrib.gis.db.models import TextField
from projfd.settings import SETTINGS_DIR

# Default indexing of database to false.
DB_INDEX = False

# override default indexing of database if appropriate
from projfd.dynamic_settings import *

class Place(Base):

    # attribution
    attribution = TextField(null=True, blank=True, db_index=DB_INDEX)

    # concordances
    enwiki_title = TextField(null=True, blank=True, db_index=DB_INDEX)
    geonames_id = IntegerField(null=True, blank=True, db_index=DB_INDEX)
    osm_id = TextField(null=True, blank=True, db_index=DB_INDEX)
    pcode = TextField(null=True, blank=True, db_index=DB_INDEX)
    fips = IntegerField(null=True, blank=True, db_index=DB_INDEX)

    # admin stuff
    admin1_code = TextField(null=True, blank=True, db_index=DB_INDEX)
    admin2_code = TextField(null=True, blank=True, db_index=DB_INDEX)
    admin3_code = TextField(null=True, blank=True, db_index=DB_INDEX)
    admin4_code = TextField(null=True, blank=True, db_index=DB_INDEX)
    admin_level = IntegerField(null=True, blank=True, db_index=DB_INDEX)

    # bounding box stuff
    east = FloatField(null=True, blank=True)
    north = FloatField(null=True, blank=True)
    south = FloatField(null=True, blank=True)
    west = FloatField(null=True, blank=True)

    # name stuff
    name = TextField(null=True, blank=True, db_index=DB_INDEX)
    name_ascii = TextField(null=True, blank=True, db_index=DB_INDEX)
    name_display = TextField(null=True, blank=True, db_index=DB_INDEX)
    name_en = TextField(null=True, blank=True, db_index=DB_INDEX)
    name_normalized = TextField(null=True, blank=True, db_index=DB_INDEX)
    other_names = TextField(null=True, blank=True, db_index=False)

    # place types
    geonames_feature_class = TextField(null=True, blank=True, db_index=DB_INDEX)
    geonames_feature_code = TextField(null=True, blank=True, db_index=DB_INDEX)
    place_type = TextField(null=True, blank=True, db_index=DB_INDEX)

    # geometries
    objects = GeoManager()
    latitude = FloatField(null=True, blank=True)
    longitude = FloatField(null=True, blank=True)
    mls = MultiLineStringField(null=True, blank=True)
    mpoly = MultiPolygonField(null=True, blank=True)
    point = PointField(null=True, blank=True)
    area_sqkm = IntegerField(null=True, blank=True)

    # osm stuff
    importance = FloatField(null=True, blank=True)
    osmname_class = TextField(null=True, blank=True, db_index=DB_INDEX)
    osmname_type = TextField(null=True, blank=True, db_index=DB_INDEX)
    osm_type = TextField(null=True, blank=True, db_index=DB_INDEX)
    place_rank = IntegerField(null=True, blank=True, db_index=DB_INDEX)

    # dem and elevation stuff
    dem = FloatField(null=True, blank=True)
    elevation = FloatField(null=True, blank=True)

    # geocoder stuff
    city = TextField(null=True, blank=True, db_index=DB_INDEX)
    county = TextField(null=True, blank=True, db_index=DB_INDEX) # should be 100
    country = TextField(null=True, blank=True, db_index=DB_INDEX)
    country_code = TextField(null=True, blank=True, db_index=DB_INDEX)
    state = TextField(null=True, blank=True, db_index=DB_INDEX)
    street = TextField(null=True, blank=True, db_index=DB_INDEX)

    #misc
    note = TextField(null=True, blank=True)
    population = BigIntegerField(null=True, blank=True, db_index=DB_INDEX)
    # number of times name appeared and meant this place minus number of times didn't mean this place
    popularity = BigIntegerField(null=True, blank=True, db_index=DB_INDEX)
    timezone = TextField(null=True, blank=True, db_index=DB_INDEX)
    topic = ForeignKey("Topic", null=True, on_delete=SET_NULL, db_index=DB_INDEX) # represents the most common topic associated with this place
    wikidata_id = TextField(null=True, blank=True, db_index=DB_INDEX)

    def get_all_names(self):
        if not hasattr(self, "all_names"):
            names = set()
            names.add(self.name)
            names.add(self.name_ascii)
            names.add(self.name_display)
            names.add(self.name_en)
            names.add(self.name_normalized)
            if self.other_names:
                for other_name in self.other_names.split(","):
                    names.add(other_name)
            names.discard(None)
            self.all_names = names
        return self.all_names

    class Meta:
        ordering = ['name']
