from appfd.models import Place
from apifd.serializers import PlaceSerializer
from broth import Broth
from appfd.conflater import conflate
import shlex
from datetime import datetime
from django.db import connection
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from multiprocessing import Process
from os.path import devnull, isfile
from os import remove
from re import IGNORECASE, match, search, sub
from requests import get
from subprocess import call
from time import sleep
from urllib.request import urlretrieve

def clean_language_name(string):
    try:
        if string in ["name_1", "name_2", "name_3", "name_4", "name_5", "name_alt", "name_int", "name_official", "name_old", "name_lang", "name_en", "name1", "name2", "name3", "name4", "name5", "name_translit", "name_historic"]:
            return "en"
        elif string in ["name_de"]:
            return "de"
        else:
            string = string.replace("&#39;", "'")
            return match("name(?:_1|_2|_3|_4|_5|_alt|_int|_official|_old|_lang|_with_accent)?:([^\"<>]*)", string).group(1)
    except Exception as e:
        print("exception in clean_language_name:", e)
        print("\tstring:", string)
        raise e


def clean_population(string):
    try:
        if string in ["-"]:
            return None
        else:
            return match("(?:(?:about|around|over) |~|<)?(?P<pop>\d+)(?: ?\((?P<year>\d+))?", string.replace(",","").replace("&#60;","<"), IGNORECASE).groupdict()['pop']
    except Exception as e:
        print("exception in clean_population:", e)
        print("\tstring:", string)
        raise e

def run(debug_level=1):

    try:

      if debug_level: start = datetime.now()

      if debug_level: print("starting to initialize osm")

      # start out testing subregion file
      for name_of_continent in ["africa", "antarctica", "asia", "australia-oceania", "central-america", "europe", "north-america", "south-america"]:
        print("\n\nname_of_continent:", name_of_continent)
        url_to_pbf = "http://download.geofabrik.de/" + name_of_continent + "-latest.osm.pbf"
        print("url_to_pbf:", url_to_pbf)
        name_of_pbf = url_to_pbf.split("/")[-1]
        if debug_level: print("name_of_pbf: " + name_of_pbf)
        path_to_pbf = "/tmp/" + name_of_pbf
        if isfile(path_to_pbf):
            print(path_to_pbf + " already exists")
        else:
            urlretrieve(url_to_pbf, path_to_pbf)
            if debug_level: print("downloaded:\n\tfrom: " + url_to_pbf + "\n\tto: " + path_to_pbf)
        

        # convert from compressed osm.pbf to o5m, which can be used by filter
        path_to_o5m = path_to_pbf.replace(".osm.pbf", ".o5m")
        if isfile(path_to_o5m):
            print(path_to_o5m + " already exists")
        else:
            command = "osmconvert " + path_to_pbf + " -o=" + path_to_o5m
            print("about to run: " + command)
            call(shlex.split(command))
            print("ran command: " + command)

        path_to_osm = path_to_o5m.replace(".o5m", ".osm")
        if isfile(path_to_osm):
            print(path_to_osm + " already exists")
        else:
            keep = "place or amenity"
            command = "osmfilter " + path_to_o5m + " --keep='" + keep + "' -o=" + path_to_osm + " --drop-author --drop-ways --drop-relations --drop-version"
            call(shlex.split(command))
            print("ran command: " + command)


        number_created = 0
        number_found = 0
        count = 0
        name = None
        aliases = []
        latitude = None
        longitude = None
        population = None
        cursor = connection.cursor()
        num_tags = 0
        num_nodes = 0
        with open(path_to_osm) as f:
            for line in f:
                count += 1
                line = line.strip()
                if debug_level >= 2: print("\n\n\nline:", [line])
                if line.startswith("<node"):
                    num_nodes += 1
                    try:
                        osm_id, latitude, longitude = match(' *<node id="(?P<id>\d+)" lat="(?P<lat>-?\d+(?:\.\d+))" lon="(?P<lon>-?\d+(?:\.\d+))"', line).groups()
                    except Exception as e:
                        print(line)
                        print(e)

                elif line.startswith("<tag"):
                    num_tags += 1
                    try:
                        key, value = match(' *<tag k="(?P<key>[^"]*)" v="(?P<value>[^"]*)"', line).groups()
                        if key and value:
                            if key.startswith("name"):
                                if key == "name":
                                    name = value
                                else:
                                    language = clean_language_name(key)
                                    aliases.append({"alias": name, "language": language})
                            elif key == "population":
                                population = clean_population(value.replace(",",""))
                            
                    except Exception as e:
                        print("\n", line)
                        print(e)
                elif line.endswith("</node>"):
                    if name and latitude and longitude:
                        conflate(name, latitude, longitude, population=population, aliases=aliases, debug_level=0, cursor=cursor)
                    aliases = []
                    name = None
                    latitude = None
                    longitude = None
                    population = None
       
                #if count >= 500000:
                #    break

        print("num_nodes:", num_nodes)
        print("num_tags:", num_tags)

        if debug_level: print("deleting files to free up disk space")
        for filepath in [path_to_pbf, path_to_o5m, path_to_osm]:
            remove(filepath)

        cursor.close()

        if debug_level:
            print("count:", count)
            duration_in_seconds = (datetime.now() - start).total_seconds()
            print("initializing osm took " + str((datetime.now() - start).total_seconds() / 60) + " minutes")
            print("rate:", count / float(duration_in_seconds))
           

    except Exception as e:

        print(e)
