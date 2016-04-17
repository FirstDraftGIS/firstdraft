from appfd.models import *
from datetime import datetime
from django.contrib.gis.geos import Point
from django.db import connection
from sys import exit

def run():
    start = datetime.now()
    print "starting loadGeoNames at ", start

    # delete all those that have a geonameid
    print "deleting all places...",
    cursor = connection.cursor()
    #cursor.execute("DELETE FROM appfd_place WHERE geonameid IS NOT NULL CASCADE") 
    cursor.execute("TRUNCATE appfd_alias CASCADE")
    cursor.execute("TRUNCATE appfd_alternatename CASCADE")
    cursor.execute("TRUNCATE appfd_place CASCADE")
    print "done"

    with open("/home/usrfd/data/geonames/allCountries.txt", "r") as f:
        counter = 0
        places_to_create = []
        for line in f:
            counter += 1

            geonameid, name, asciiname, alternatenames, latitude, longitude, feature_class, feature_code, country_code, cc2, admin1_code, admin2_code, admin3_code, admin4_code, population, elevation, dem, timezone, modification_date = line.split("\t")

            places_to_create.append(Place(id=counter, admin_level=None, admin1_code=admin1_code, admin2_code=admin2_code, country_code=country_code, geonameid=geonameid, name=name, point=Point(x=float(longitude), y=float(latitude)), population=float(population), timezone=timezone))

            if counter % 100000 == 0:
                Place.objects.bulk_create(places_to_create)
                places_to_create = []
                print "created and reset places_to_create to blank"

    end = datetime.now()
    total_seconds = (end - start).total_seconds()
    message = "Loading geonames took " + str(total_seconds) + " seconds."
    print message
    with open("log.txt", "wb") as f:
        f.write(message)
        
