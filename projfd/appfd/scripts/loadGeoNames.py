from models import *

def run():
    print "running loadGeoNames"
    counter = 0
    with open("/home/usrfd/data/geonames/allCountries.txt", "r") as f:
        for line in f:
            print "line is", line

#            place = Place.objects.create(geonameid= 

            if counter == 10:
                break
            else:
               counter += 1
