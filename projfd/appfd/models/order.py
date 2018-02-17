#-*- coding: utf-8 -*-
from .base import Base
from datetime import datetime
from django.contrib.gis.db.models import BooleanField
from django.contrib.gis.db.models import CharField
from django.contrib.gis.db.models import DateTimeField
from django.contrib.gis.db.models import SET_NULL
from django.contrib.gis.db.models import ForeignKey
from django.contrib.gis.db.models import IntegerField
from django.contrib.gis.db.models import URLField
from django.contrib.auth.models import User
from shutil import rmtree

class Order(Base):
    complete = BooleanField(default=False)
    duration = IntegerField(null=True) # how long it took to process the order
    edited = BooleanField(default=False) # tells you whether they opened it for editing... not whether any actual edits were made
    end = DateTimeField(null=True)
    end_user_timezone = CharField(max_length=20, null=True)
    map_format = CharField(max_length=20, null=True)
    open_source = BooleanField(default=False) #is this map open-sourced, such that it can be included in open source training data?
    start = DateTimeField(auto_now_add=True, null=True) # it will never be null, but have to do this because migration asks for default otherwise
    style = ForeignKey("MapStyle", null=True, on_delete=SET_NULL)
    token = CharField(max_length=200, null=True, unique=True) # the random string that's used to find the order in the maps
    url = URLField(null=True, max_length=1000, unique=True) # URL if started from url or iframe embeded on a webpage

    def __str__(self):
        return self.token

    def d(self):
        self.delete_map()
        self.delete()

    def delete_map(self):
        rmtree("/home/usrfd/maps/" + self.token)

    def finish(self):
        self.complete = True
        self.end = end = datetime.now().replace(tzinfo=utc)
        self.duration = (end - self.start).total_seconds()
        self.save()
