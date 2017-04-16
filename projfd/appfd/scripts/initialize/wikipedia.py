from appfd.models import Place, Wikipedia
from broth import Broth
import csv
from datetime import datetime
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from multiprocessing import Process
from os.path import devnull, isfile
from os import remove
from re import match, search
from requests import get
from subprocess import call
from time import sleep

def run(debug=True):

    try:

        if debug: start = datetime.now()

        if debug: print "starting to initialize wikipedia"

        with open("/tmp/notability.tsv") as f:
            count = 0
            for row in csv.reader(f, delimiter="\t", quotechar='"'):
                try:
                    count += 1
                    if count != 1:
                        name, latitude, longitude, charcount = row
                        places = Place.objects.filter(name=name)
                        #print "places:", places
                        point = Point([float(longitude), float(latitude)])
                        found = places.filter(point__distance_lt=(point, Distance(mi=500)))
                        if not found:
                            found = places.filter(mpoly__contains=point)
                        if found.count() > 1:
                            filtered = found.exclude(population=0)
                            if filtered:
                                found = filtered
                            if found.count() > 1:
                                found = found.exclude(admin_level=None)
                        #    print "found within:", found
                        #print name, ":", found.values("admin_level","population").count(), ":", charcount
                        place = found.first()
                        if not place:
                            place = Place.objects.create(name=name, point=point)
                            #print "created:", place
                        Wikipedia.objects.get_or_create(place_id=place.id, charcount=charcount)
                        if count > 500:
                            break
                except Exception as e:
                    print e
            

        if debug: print "initializing wikipedia took " + str((datetime.now() - start).total_seconds()) + " seconds"

    except Exception as e:

        print e
