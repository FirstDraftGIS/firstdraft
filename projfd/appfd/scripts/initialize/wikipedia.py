from appfd.models import Place, Wikipedia
from apifd.serializers import PlaceSerializer
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
from urllib import urlretrieve

def run(debug=True):

    try:

        if debug: start = datetime.now()

        if debug: print "starting to initialize wikipedia"

        path_to_tsv = "/tmp/notability.tsv"
        if not isfile(path_to_tsv):
            urlretrieve("https://raw.githubusercontent.com/DanielJDufour/geo_notability_assessor/master/notability.tsv", path_to_tsv)

        if debug: print "opening tsv"
        number_created = 0
        number_found = 0
        with open(path_to_tsv) as f:
            count = 0
            for row in csv.reader(f, delimiter="\t", quotechar='"'):
                try:
                    count += 1
                    if count != 1:
                        name, latitude, longitude, charcount = row
                        if debug: print "\n\n\nrow:", row
                        if latitude and longitude:
                            places = Place.objects.filter(name=name)
                            #print "places:", places
                            try:
                                point = Point([float(longitude), float(latitude)])
                            except Exception as e:
                                print "e:", e
                                print "\tlongitude:", longitude
                                print "\tlatitude:", latitude

                            found_places = places.filter(point__distance_lt=(point, Distance(mi=500)))
                            if debug: print "found via point distance:", found_places

                            if not found_places:
                                found_places = places.filter(mpoly__contains=point)
                                if debug: print "found via mpoly__contains:", found_places

                            if found_places.count() > 1:
                                found_via_pop = found_places.exclude(population=0).exclude(population=None)
                                if debug: print "found_via_pop:", found_via_pop
                                if found_via_pop:
                                    found_places = found_via_pop


                                if found_via_pop.count() > 1:
                                    matches_with_admin_level = found_places.exclude(admin_level=None)
                                    if debug: print "found by excluding those without an admin_level:", matches_with_admin_level
                                    if matches_with_admin_level:
                                        found_places = matches_with_admin_level
                                    
                            #    print "found within:", found
                            place = found_places.first()
                            if place:
                                number_found += 1
                                if debug: print "found place:", PlaceSerializer(place).data
                            else:
                                number_created += 1
                                place = Place.objects.create(name=name, point=point)
                                if debug: print "created place:", place
                            wikipedia, created = Wikipedia.objects.get_or_create(place_id=place.id, charcount=charcount)
                            print ("created" if created else "got"), "wikipedia", wikipedia
                            #if count > 10000:
                            #    break
                except Exception as e:
                    print e
            

        if debug:
            print "number_created:", number_created
            print "number_found:", number_found
            print "found %:", float(number_found) / (number_found + number_created) * 100, "%"
            print "initializing wikipedia took " + str((datetime.now() - start).total_seconds() / 60) + " minutes"

    except Exception as e:

        print e
