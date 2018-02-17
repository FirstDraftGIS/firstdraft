#-*- coding: utf-8 -*-
from .base import Base
from django.contrib.gis.db.models import BigIntegerField
from django.contrib.gis.db.models import CharField
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
    attribution = CharField(max_length=500, null=True, blank=True)

    # concordances
    enwiki_title = TextField(max_length=175, null=True, blank=True, db_index=DB_INDEX)
    geonames_id = IntegerField(null=True, blank=True, db_index=DB_INDEX)
    osm_id = CharField(max_length=15, null=True, blank=True)
    pcode = CharField(max_length=200, null=True, blank=True, db_index=DB_INDEX)
    fips = IntegerField(null=True, blank=True, db_index=DB_INDEX)

    # admin stuff
    admin1_code = CharField(max_length=10, null=True, blank=True, db_index=DB_INDEX)
    admin2_code = CharField(max_length=65, null=True, blank=True, db_index=DB_INDEX)
    admin3_code = CharField(max_length=15, null=True, blank=True, db_index=DB_INDEX)
    admin4_code = CharField(max_length=15, null=True, blank=True, db_index=DB_INDEX)
    admin_level = IntegerField(null=True, blank=True, db_index=DB_INDEX)

    # bounding box stuff
    east = FloatField(null=True, blank=True)
    north = FloatField(null=True, blank=True)
    south = FloatField(null=True, blank=True)
    west = FloatField(null=True, blank=True)

    # name stuff
    name = CharField(max_length=250, null=True, blank=True)
    name_ascii = CharField(max_length=1500, null=True, blank=True)
    name_display = CharField(max_length=350, null=True, blank=True)
    name_en = CharField(max_length=250, null=True, blank=True)
    name_normalized = CharField(max_length=2000, null=True, blank=True, db_index=DB_INDEX)
    other_names = TextField(max_length=18873, null=True, blank=True)

    # place types
    geonames_feature_class = CharField(max_length=1, null=True, blank=True, db_index=DB_INDEX)
    geonames_feature_code = CharField(max_length=5, null=True, blank=True, db_index=DB_INDEX)
    place_type = CharField(max_length=1, null=True, blank=True)

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
    osmname_class = CharField(max_length=10, null=True, blank=True)
    osmname_type = CharField(max_length=160, null=True, blank=True)
    osm_type = CharField(max_length=106, null=True, blank=True)
    place_rank = IntegerField(null=True, blank=True)

    # dem and elevation stuff
    dem = FloatField(null=True, blank=True)
    elevation = FloatField(null=True, blank=True)

    # geocoder stuff
    city = CharField(max_length=114, null=True, blank=True)
    county = CharField(max_length=100, null=True, blank=True)
    country = CharField(max_length=40, null=True, blank=True)
    country_code = CharField(max_length=2, null=True, blank=True, db_index=DB_INDEX)
    state = CharField(max_length=120, null=True, blank=True)
    street = CharField(max_length=203, null=True, blank=True)

    #misc
    note = CharField(max_length=200, null=True, blank=True)
    population = BigIntegerField(null=True, blank=True)
    # number of times name appeared and meant this place minus number of times didn't mean this place
    popularity = BigIntegerField(null=True, blank=True)
    timezone = CharField(max_length=30, null=True, blank=True, db_index=DB_INDEX)
    topic = ForeignKey("Topic", null=True, on_delete=SET_NULL) # represents the most common topic associated with this place

    class Meta:
        ordering = ['name']
