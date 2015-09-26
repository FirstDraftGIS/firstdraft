from appfd.models import *
from django.contrib.gis.gdal import DataSource
import os, urllib, zipfile
from urllib import urlretrieve

def run():

    if not os.path.isfile('/tmp/alternateNames.zip'):
        urlretrieve('http://download.geonames.org/export/dump/alternateNames.zip', '/tmp/alternateNames.zip')
        with zipfile.ZipFile('/tmp/alternateNames.zip', "r") as z:
            z.extractall('/tmp/')

    with open('/tmp/alternateNames.txt') as f:
        for index, line in enumerate(f):
          try:
            line_split = line.decode("utf-8").strip().split("\t")
            geonameid = int(line_split[0])
            language = line_split[2]
            alternate_name = line_split[3]
            
            #if index == 200:
            #    break

            if language != "link":
                print "line ", index, ": ", line_split

                alias = Alias.objects.get_or_create(alias=alternate_name)[0]
                alias.language = language[:2]
                alias.save()

                place = Place.objects.get(geonameid=geonameid)

                AliasPlace.objects.get_or_create(alias=alias, place=place)
          except Exception as e:
            print e
