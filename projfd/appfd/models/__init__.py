#-*- coding: utf-8 -*-
from .base import Base

from datetime import datetime
from django.core.validators import RegexValidator
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib.gis.db.models import CASCADE, DO_NOTHING
from django.contrib.gis.db.models import *
from pytz import utc
from shutil import rmtree

# import other models
from .activation import Activation
from .alert import Alert
from .order import Order
from .place import Place

#class Account(Model):
#    max_orders = IntegerField() # the maximum number of order this account can make per month

# abstraction of who authored the content
# different than who provided the content
# for example, John might ask to geocode a tweet by Maria.
# Maria is the author in that case.
# We're abstracting it from just Tweeter because we don't
# know if Twitter will last forever and want Machine Learning
# data that will be useful for a long time
# For twitter, the Author will be the twitter username
class Author(Base):
    # twitter handle
    short_name = CharField(max_length=20)

    # verbose name
    verbose_name = CharField(max_length=100)

    def __str__(self):
        return self.name

class AlternateName(Model):
    geonameid = IntegerField(db_index=True)
    isolanguage = CharField(max_length=7, null=True, blank=True)
    alternate_name = CharField(max_length=200, null=True, blank=True, db_index=True)
    isPreferredName = CharField(max_length=1, null=True, blank=True)
    isShortName = CharField(max_length=1, null=True, blank=True)
    isColloquial = CharField(max_length=1, null=True, blank=True)
    isHistoric = CharField(max_length=1, null=True, blank=True)

class Basemap(Base):
    name = CharField(max_length=50)
    def __str__(self):
        return self.name

class Cooccurrence(Model):
    a = IntegerField() # actually a fk to place, but don't want restraints
    b = IntegerField()
    count = IntegerField()
    def __str__(self):
        return str(self.a) + " & " + str(self.b) + ": " + str(self.count)

class CountryCodeRank(Base):
    country_code = CharField(max_length=10, null=True)
    rank = IntegerField(null=True)
    order = ForeignKey("order", to_field="token", on_delete=CASCADE)

    class Meta:
        unique_together = (("country_code","order"))

class Calls(Base):
    date = DateField()
    total = IntegerField(default=0)
    CHOICES = [('gt', "Google Translate API")]
    service = CharField(max_length=200, choices=CHOICES)

class Alias(Base):
    alias = CharField(max_length=200, null=True, blank=True, db_index=True, unique=True)
    language = CharField(max_length=7, null=True, blank=True, db_index=True)
    class Meta:
        ordering = ['alias']
    def __str__(self):
        return self.alias.encode("utf-8")

class AliasPlace(Base):
    alias = ForeignKey('Alias', on_delete=CASCADE)
    place = ForeignKey('Place', on_delete=CASCADE)

    class Meta:
        unique_together = (("alias","place"))


class Email(Base):
    address = EmailField(null=True, blank=True)
    entered = DateTimeField(auto_now_add=True)

class MetaData(Base):
    order = ForeignKey("Order", on_delete=CASCADE)

class MetaDataEntry(Base):
    metadata = ForeignKey("Metadata", on_delete=CASCADE)
    key = CharField(max_length=255)
    value = TextField(max_length=2000)

    def __str__(self):
        return "[" + str(self.metadata.id) + "] " + str(self.key)

### this is what consitutes the FeatureCollection of the map
class Feature(Base):
    order = ForeignKey("Order", on_delete=CASCADE)
    count = IntegerField(null=True) # number of times the thing was mentioned in the text
    end = DateTimeField(null=True)
    name = CharField(max_length=255)
    geometry_used = CharField(max_length=100, default="Point") #"Point", "Polygon" or "Point & Polygon"
    start = DateTimeField(null=True)
    text = TextField(max_length=1000, null=True)
    topic = ForeignKey("Topic", null=True, on_delete=SET_NULL)
    verified = BooleanField(default=False) # has a user verified this... we just go by whether a user has taken an action that implies they verified this such as downloading the map or clicking share
    # should probably include some styling information at some point
    # maybe should add in info about whether use point or polygon info
    def __str__(self):
        return str([self.order.token + "|" + self.name])

class FeaturePlace(Base):
    feature = ForeignKey("Feature", on_delete=CASCADE)
    place = ForeignKey("Place", on_delete=CASCADE)
    cluster_frequency = FloatField(null=True)
    confidence = DecimalField(max_digits=5, decimal_places=4)
    country_rank = IntegerField(null=True)
    correct = NullBooleanField(null=True)
    median_distance = FloatField(null=True)
    sort_order = IntegerField(null=True)
    popularity = IntegerField(null=True)
    def __str__(self): 
        return str(self.feature.id) + "~" + str(self.place.id)

# styles and info that apply to a map as a whole
try:
    default_basemap_id = Basemap.objects.get(name="OpenStreetMap.Mapnik").id
except:
    default_basemap_id = None
class MapStyle(Base):
    basemap = ForeignKey("Basemap", default=default_basemap_id, null=True, on_delete=SET_DEFAULT)

class ParentChild(Base):
    parent = ForeignKey('Place', related_name="parentplace", on_delete=CASCADE)
    child = ForeignKey('Place', related_name="subplace", on_delete=CASCADE)

    #makes sure we can't repeat parent child in db
    class Meta:
        unique_together = (("parent","child"))

# this is the source data, not the attribution
class Source(Base):
    order = ForeignKey("order", on_delete=CASCADE)
    source_text = CharField(max_length=2000, null=True)
    source_type = CharField(max_length=200)
    source_url = URLField(max_length=2000, null=True)

    def __str__(self):
        representation = "[" + str(self.order.token) + "]"
        if self.source_type == "url":
            representation += " : " + self.source_url
        elif self.source_type == "text":
            representation += " : " + self.source_text
        return representation 

class Style(Base):
    feature = ForeignKey("feature", on_delete=CASCADE)
    fill = CharField(max_length=30, null=True)
    fillOpacity = FloatField(null=True)
    label = BooleanField(default=False)
    #labelOpacity = FloatField(null=True)
    stroke = CharField(max_length=30, null=True)
    strokeOpacity = FloatField(null=True)
    strokeWidth = IntegerField(null=True)

    def __str__(self):
        return "(" + str(self.id) + ") " + self.feature.name + "'s style"


class TeamMember(Base):
    email = EmailField(null=True, blank=True)
    name = CharField(max_length=200, null=True, blank=True)
    pic = ImageField(upload_to="images/topicareas", null=True, blank=True)
    position = CharField(max_length=200, null=True, blank=True)
    twitter = CharField(max_length=200, null=True, blank=True)

class Test(Base):
    accuracy = FloatField()
    duration = IntegerField()

    def __str__(self):
        return str(self.created) + " with accuracy of " + str(self.accuracy)

class Topic(Base):
    name = TextField(max_length=50, null=True, blank=True)

class Translator(Base):
    name = CharField(max_length=200, null=True, blank=True)
