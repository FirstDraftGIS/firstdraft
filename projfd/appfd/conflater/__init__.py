from appfd.models import Place, Wikipedia
from apifd.serializers import VerbosePlaceSerializer
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

def conflate(name, latitude, longitude, population=None, aliases=None, debug_level=False):

    try:

        if debug_level: start = datetime.now()

        if debug_level:
            print "starting conflate with:"
            print "\tname:", name
            print "\tlatitude:", latitude
            print "\tlongitude:", longitude

        if debug_level >= 1:
            import logging
            l = logging.getLogger('django.db.backends')
            l.setLevel(logging.DEBUG)
            l.addHandler(logging.StreamHandler())


        if latitude and longitude:
            lat = str(latitude)
            lon = str(longitude)
            pop = str(population) if population else "NULL"
            print [lat, lon, pop]
            places = Place.objects.raw("""
    WITH data AS (SELECT
        *,
        ST_DWithin(CAST(ST_SetSRID(ST_Point(""" + lon + """, """ + lat + """), 4326) As geography), point, 1) AS d1,
        ST_DWithin(CAST(ST_SetSRID(ST_Point(""" + lon + """, """ + lat + """), 4326) As geography), point, 10) AS d10,
        ST_DWithin(CAST(ST_SetSRID(ST_Point(""" + lon + """, """ + lat + """), 4326) As geography), point, 100) AS d100,
        ST_DWithin(CAST(ST_SetSRID(ST_Point(""" + lon + """, """ + lat + """), 4326) As geography), point, 1000) AS d1000,
        ST_DWithin(CAST(ST_SetSRID(ST_Point(""" + lon + """, """ + lat + """), 4326) As geography), point, 10000) AS d10000,
        """ + pop + """ IS NOT NULL AS pop_exists,
        CASE WHEN """ + pop + """ IS NOT NULL AND population > 0 THEN abs(""" + pop + """ - population)::decimal / GREATEST(""" + pop + """, population)::decimal < 0.05 ELSE false END AS pop_is_close,
        admin_level IS NOT NULL AS has_admin_level

    FROM appfd_place WHERE name = '""" + name + """')
    SELECT
        *,
        d1::int * 10000 +
        d10::int * 1000 +
        d100::int * 100 +
        d1000::int * 10 +
        d10000::int * 1 +
        pop_exists::int * 10 +
        pop_is_close::int * 1000
        AS score
        FROM data
        WHERE d1 IS true OR d10 is true or d100 is true or d1000 is true or d10000 is true
        ORDER BY score DESC;
            """)

        if debug_level:
            print "conflation took " + str((datetime.now() - start).total_seconds()) + " seconds"
            raw_input("press any key to continue")
        try:
            return places[0]
        except:
            return None

    except Exception as e:

        print e
