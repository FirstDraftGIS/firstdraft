#from appfd.models import Feature, Place
from appfd.models import *
from appfd.scripts.ai import predict
from collections import Counter, defaultdict
#from geojson import Feature, FeatureCollection, MultiPolygon, Point
from datetime import datetime
from django.contrib.gis.geos import GEOSGeometry
from django.db import connection
from django.db.models import Q
import editdistance
from multiprocessing import *
from numpy import amin, argmin, mean, median
from random import shuffle
from scipy.spatial.distance import cdist
from super_python import *
from sys import exit
from timeit import default_timer
from time import sleep


# choose place by distance from all other places 
def filter_dict_by_distance(dict_of_places_by_name):
    print("starting filter_dict_by_distance", dict_of_places_by_name)
    start = datetime.now()

    all_coords = []
    places = []
    for options in dict_of_places_by_name.values():
        places.extend([option['place'] for option in options])
        all_coords.extend([option['place'].point.coords for option in options])

    for name in dict_of_places_by_name:
        try: print "name_of_place:", name
        except Exception as e: print e
        places_for_name = dict_of_places_by_name[name]
        print "places_for_name:", places_for_name
        if len(places_for_name) > 1:
            option_coords = [dic['place'].point.coords for dic in places_for_name]
            dict_of_places_by_name[name] = places_for_name[argmin(median(cdist(option_coords, all_coords), axis=1))]['place']
        else:
            dict_of_places_by_name[name] = places_for_name[0]['place']
   
    #print "\n\n\nfilter_dict_by_distance took:", (datetime.now()-start).total_seconds(), "seconds\n\n\n"  
    return dict_of_places_by_name.values()

class GeoEntity(object):

    def __init__(self, row):
        self.place_id = row[0]
        self.admin_level = str(row[1])
        self.country_code = row[2]
        self.country_rank = row[3]
        self.target, self.edit_distance = row[4].split("--")
        self.edit_distance = int(self.edit_distance)
        self.place_name = row[5]
        self.alias = row[6]
        self.population = row[7]
        self.point = GEOSGeometry(row[8])

# takes in a list of locations and resovles them to features in the database
def resolve_locations(locations, max_seconds=86400):
  try:
    print "starting resolve_locations with", type(locations)
    print "locations = ", len(locations), locations[:5]

    start = datetime.now()

    names = [location['name'] for location in locations]
    print "names", len(names), names[:5]

    # randomize order in order to minimize statistic bias
    shuffle(names)

    names = set(names)

    cursor = connection.cursor()

    statement = "SELECT * FROM fdgis_resolve('{" + ", ".join(names) + "}'::TEXT[]);"
    print statement
    cursor.execute(statement)

    geoentities = [GeoEntity(row) for row in cursor.fetchall()]

    print "geoentities", type(geoentities)

    # calculate median distance from every other point
    #all_cords = [geoentity.point.coords for geoentity in geoentities]

    target_geoentities = defaultdict(list)
    target_coords = defaultdict(list)
    all_coords = []
    for geoentity in geoentities:
        all_coords.append(geoentity.point.coords)
        target_geoentities[geoentity.target].append(geoentity)
        target_coords[geoentity.target].append(geoentity.point.coords)

    print("target_geoentities:", target_geoentities)
    for target, options in target_geoentities.items():
        print "target:", target
        for i, v in enumerate(median(cdist(target_coords[target], all_coords), axis=1)):
            target_geoentities[target][i].median_distance_from_all_other_points = v

    predict.run(geoentities)

    print "took:", (datetime.now() - start).total_seconds()

    """
    locations_by_name = dict([(location['name'], location) for location in locations])
    features = []
    for name in d:
        feature = Feature()
        _dict = d[name] 
        feature.place = place = _dict['place']

        if name in locations_by_name:
            location = locations_by_name[name]
        elif place.alias in locations_by_name:
            location = locations_by_name[place.alias]

        feature.confidence = _dict['confidence']

        feature.count = location['count']

        if not place.point:
            try:
                place.update({"point": place.mpoly.centroid})
            except AttributeError as e:
                if e.message == "'NoneType' object has no attribute 'centroid'":
                    continue
                else:
                    raise e

        if "date" in location:
            feature.end = location['date']
            feature.start = location['date']
        if "context" in location:
            feature.text = location['context'][:1000]
        features.append(feature)

    print "features final are", len(features)

    return features
    """

  except Exception as e:
    print e
