from appfd.models import Place
from datetime import datetime
from django.db import connection

def conflate(name, latitude, longitude, population=None, aliases=None, debug_level=False, cursor=None, return_id_only=True):

    try:

        if debug_level: start = datetime.now()

        if debug_level >= 2:
            print "starting conflate with:"
            print "\tname:", name
            print "\tlatitude:", latitude
            print "\tlongitude:", longitude

        if debug_level >= 2:
            import logging
            l = logging.getLogger('django.db.backends')
            l.setLevel(logging.DEBUG)
            l.addHandler(logging.StreamHandler())


        if latitude and longitude:
            country_code = "NULL"
            population = str(population) if population else "NULL"
       
            statement = "SELECT id FROM conflate_and_return_place('" + name + "'," + str(latitude) + "," + str(longitude) + "," + country_code + "," + population + ")"
            print "statement:", statement
            if cursor: 
                cursor.execute(statement)
                place_id = cursor.fetchall()[0][0]
            #else:
            #    place = list(Place.objects.raw(statement))[0]
            
        if debug_level:
            print "conflation took " + str((datetime.now() - start).total_seconds()) + " seconds"
            print "place:", place
            raw_input("press any key to continue")

        return place_id

    except Exception as e:
        print e
        print "name:", name
        print "\tlatitude:", latitude
        print "\tlongitude:", longitude
        print "\tcountry_code:", country_code
        print "\tpopulation:", population


