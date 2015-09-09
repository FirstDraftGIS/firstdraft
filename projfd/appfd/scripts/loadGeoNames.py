from appfd.models import *
from django.contrib.gis.geos import Point

def run():
    print "running loadGeoNames"

    Place.objects.all().delete()

    counter = 0
    with open("/home/usrfd/data/geonames/allCountries.txt", "r") as f:
        for line in f:
            #print "line is", line
            line_split = line.strip().split("\t")
            #print "line_split is", line_split
            #print "geonameid = ", int(line_split[0])
            place = Place.objects.create(geonameid=int(line_split[0]))
            place.name = line_split[1]
            #print "place.name is", line_split[1]
            place.point = Point(x=float(line_split[5]),y=float(line_split[4])) 
            place.save()

            if counter % 1000 == 0:
                print ".",
            else:
               counter += 1
