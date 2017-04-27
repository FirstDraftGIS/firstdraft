from datetime import datetime
from django.db import connection

def conflate(name, latitude, longitude, population=None, aliases=None, debug_level=False, cursor=None):

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
        
            statement = "SELECT conflate('" + name + "'," + str(latitude) + "," + str(longitude) + "," + country_code + "," + population + ")"
            if debug_level: print "statement:", statement
            if cursor:
                cursor.execute(statement)
            else:
                with connection.cursor() as cursor:
                    cursor.execute(statement)
            
        if debug_level:
            print "conflation took " + str((datetime.now() - start).total_seconds()) + " seconds"
            raw_input("press any key to continue")

    except Exception as e:
        print e
        print "name:", name
        print "\tlatitude:", latitude
        print "\tlongitude:", longitude
        print "\tcountry_code:", country_code
        print "\tpopulation:", population


