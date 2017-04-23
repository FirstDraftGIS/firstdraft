from appfd.models import Place
from apifd.serializers import PlaceSerializer
from broth import Broth
from appfd.conflater import conflate
import shlex
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

        if debug: print "starting to initialize osm"

        # start out testing subregion file
        url_to_pbf = "https://download.geofabrik.de/north-america/us/district-of-columbia-latest.osm.pbf"
        name_of_pbf = url_to_pbf.split("/")[-1]
        if debug: print "name_of_pbf: " + name_of_pbf
        path_to_pbf = "/tmp/" + name_of_pbf
        if not isfile(path_to_pbf):
            urlretrieve(url_to_pbf, path_to_pbf)
            if debug: print "downloaded:\n\tfrom: " + url_to_pbf + "\n\tto: " + path_to_pbf

        # convert from compressed osm.pbf to o5m, which can be used by filter
        path_to_o5m = path_to_pbf.replace(".osm.pbf", ".o5m")
        command = "osmconvert " + path_to_pbf + " -o=" + path_to_o5m
        call(shlex.split(command))
        print "ran command: " + command

        path_to_osm = path_to_o5m.replace(".o5m", ".osm")
        keep = "place or amenity"
        command = "osmfilter " + path_to_o5m + " --keep='" + keep + "' -o=" + path_to_osm + " --drop-author --drop-ways --drop-relations --drop-version"
        call(shlex.split(command))
        print "ran command: " + command


        number_created = 0
        number_found = 0
        count = 0
        name = None
        latitude = None
        longitude = None
        with open(path_to_osm) as f:
            for line in f:
                count += 1
                line = line.strip()
                if debug: print "\nline:", [line]
                if line.startswith("<node"):
                    try:
                        osm_id, latitude, longitude = match(' *<node id="(?P<id>\d+)" lat="(?P<lat>-?\d+(?:\.\d+))" lon="(?P<lon>-?\d+(?:\.\d+))"', line).groups()
                    except Exception as e:
                        print line
                        print e

                elif line.startswith("<tag"):
                    try:
                        key, value = match(' *<tag k="(?P<key>[^"]+)" v="(?P<value>[^"]+)"', line).groups()
                        if key == "name":
                            name = value
                            print "set name to ", value
                    except Exception as e:
                        print "\n", line
                        print e
                elif line.endswith("</node>"):
                    if name and latitude and longitude:
                        conflate(name, latitude, longitude)
                    name = None
                    latitude = None
                    longitude = None
       
                if count >= 50000000000:
                    break

        if debug:
            print "initializing osm took " + str((datetime.now() - start).total_seconds() / 60) + " minutes"

    except Exception as e:

        print e
