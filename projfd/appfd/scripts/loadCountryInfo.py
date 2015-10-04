from appfd.models import *
from bnlp import trim_location
from django.contrib.gis.gdal import DataSource
import os, urllib, zipfile
from urllib import urlretrieve

def run():
    pathToCountryInfoFile = '/tmp/countryInfo.txt' 

    if not os.path.isfile(pathToCountryInfoFile):
        urlretrieve('http://download.geonames.org/export/dump/countryInfo.txt', pathToCountryInfoFile)

    with open(pathToCountryInfoFile, 'r') as f:
        found_header = False
        for line in f:
            if found_header:
                try: 
                    line_split = line.split("\t")
                    geonameid = line_split[16]
                    place = Place.objects.get(geonameid=geonameid)
                    place.admin_level = 0
                    place.name = trim_location(place.name)
                    place.save()
                except Exception as e:
                    print e
            elif line.count("\t") > 5 and "Languages" in line and "fips" in line:
                found_header = True
        
