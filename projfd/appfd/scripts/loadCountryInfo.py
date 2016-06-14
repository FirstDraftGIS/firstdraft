from appfd.models import *
from datetime import datetime
from bnlp import trim_location
from django.contrib.gis.gdal import DataSource
from os.path import isfile
from urllib import urlretrieve

def run():
    print "starting loadCountryInfo"
    start = datetime.now()
    pathToCountryInfoFile = '/tmp/countryInfo.txt' 

    if not isfile(pathToCountryInfoFile):
        urlretrieve('http://download.geonames.org/export/dump/countryInfo.txt', pathToCountryInfoFile)

    with open(pathToCountryInfoFile, 'r') as f:
        found_header = False
        for line in f:
            if found_header:
              try: 
                print "split is", line.split("\t")
                iso, iso3, iso_numeric, fips, country, capital, area_sqkm, population, continent, tld, currency_code, currency_name, phone, postal_code_format, postal_code_regex, languages, geonameid, neighbours, equivalent_fips_code = line.split("\t")
                Place.objects.filter(geonameid=geonameid).update(admin_level=0, name=country)
              except Exception as e:
                print e
            elif line.count("\t") > 5 and "Languages" in line and "fips" in line:
                found_header = True
       
    end = datetime.now()
    total_seconds = (end - start).total_seconds()
    print "total_seconds = ", total_seconds
    with open("log.txt", "a") as f:
        f.write("Loading countryInfo took " + str(total_seconds) + " seconds.")
