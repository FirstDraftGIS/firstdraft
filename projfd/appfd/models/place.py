#-*- coding: utf-8 -*-
from base import Base
from django.contrib.gis.db.models import *

class Place(Base):
    admin1_code = CharField(max_length=100, null=True, blank=True, db_index=True)
    admin2_code = CharField(max_length=100, null=True, blank=True, db_index=True)
    admin3_code = CharField(max_length=100, null=True, blank=True, db_index=True)
    admin4_code = CharField(max_length=100, null=True, blank=True, db_index=True)
    admin_level = IntegerField(null=True, blank=True, db_index=True)
    area_sqkm = IntegerField(null=True, blank=True)
    asciiname = CharField(max_length=1000, null=True, blank=True)
    attribution = CharField(max_length=1000, null=True, blank=True)
    city = CharField(max_length=1000, null=True, blank=True)
    county = CharField(max_length=1000, null=True, blank=True)
    country = CharField(max_length=1000, null=True, blank=True)
    country_code = CharField(max_length=2, null=True, blank=True, db_index=True)
    dem = FloatField(null=True, blank=True)
    display_name = CharField(max_length=12345, null=True, blank=True)
    district_num = IntegerField(null=True, blank=True)
    east = FloatField(null=True, blank=True)
    elevation = FloatField(null=True, blank=True)
    enwiki_title = TextField(max_length=5000, null=True, blank=True)
    fips = IntegerField(null=True, blank=True, db_index=True)
    geonames_feature_class = CharField(max_length=50, null=True, blank=True, db_index=True)
    geonames_feature_code = CharField(max_length=50, null=True, blank=True, db_index=True)
    geonames_id = IntegerField(null=True, blank=True, db_index=True)
    importance = FloatField(null=True, blank=True)
    latitude = FloatField(null=True, blank=True)
    longitude = FloatField(null=True, blank=True)
    mls = MultiLineStringField(null=True, blank=True)
    mpoly = MultiPolygonField(null=True, blank=True)
    name = CharField(max_length=2000, null=True, blank=True, db_index=True)
    name_en = CharField(max_length=2000, null=True, blank=True, db_index=True)
    north = FloatField(null=True, blank=True)
    note = CharField(max_length=200, null=True, blank=True)
    objects = GeoManager()
    other_names = TextField(max_length=100000, null=True, blank=True)
    osm_id = CharField(max_length=106, null=True, blank=True)
    osmname_class = CharField(max_length=1000, null=True, blank=True)
    osmname_type = CharField(max_length=1000, null=True, blank=True)
    osm_type = CharField(max_length=106, null=True, blank=True)
    pcode = CharField(max_length=200, null=True, blank=True, db_index=True)
    place_rank = IntegerField(null=True, blank=True)
    place_type = CharField(max_length=1, null=True, blank=True)
    point = PointField(null=True, blank=True)
    population = BigIntegerField(null=True, blank=True)

    # number of times name appeared and meant this place minus number of times didn't mean this place
    popularity = BigIntegerField(null=True, blank=True)

    skeleton = MultiLineStringField(null=True, blank=True)
    south = FloatField(null=True, blank=True)
    state = CharField(max_length=1000, null=True, blank=True)
    street = CharField(max_length=1000, null=True, blank=True)
    timezone = CharField(max_length=200, null=True, blank=True, db_index=True)
    topic = ForeignKey("Topic", null=True) # represents the most common topic associated with this place
    west = FloatField(null=True, blank=True)

    class Meta:
        ordering = ['name']
