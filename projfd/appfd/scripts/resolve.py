#from appfd.models import Feature, Place
from appfd.models import *
from appfd.scripts.ai import predict
from collections import Counter, defaultdict
from decimal import Decimal
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
def resolve_locations(locations, order_id, max_seconds=86400):
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

    print("target_geoentities:", len(target_geoentities))
    for target, options in target_geoentities.items():
        print "target:", target
        for i, v in enumerate(median(cdist(target_coords[target], all_coords), axis=1)):
            if v is None:
                print "v is NONE!!!!"
                exit()
            target_geoentities[target][i].median_distance_from_all_other_points = int(v)

    # this method adds the probability to each geoentity
    predict.run(geoentities)

    # need to choose one for each target based on highest probability
    for target, options in target_geoentities.items():
        max_probability = max([o.probability for o in options])
        found_correct = False
        for option in options:
            if not found_correct and option.probability == max_probability:
                option.correct = True
                found_correct = True
            else:
                option.correct = False
 
    #Feature, FeaturePlace
    featureplaces = [] 
    for target, options in target_geoentities.items():
        l = [l for l in locations if l['name'] == target][0]
        feature = Feature.objects.create(count=l['count'], name=target, geometry_used="Point", order_id=order_id, text=l['context'], verified=False) 
        if "date" in location:
            feature.end = location['date']
            feature.start = location['date']
        for option in options:
            featureplaces.append(FeaturePlace(confidence=float(option.probability), correct=option.correct, feature=feature, median_distance=option.median_distance_from_all_other_points, place_id=option.place_id))

    FeaturePlace.objects.bulk_create(featureplaces)

    print "resolved locations for order " + str(order_id)

    print "took:", (datetime.now() - start).total_seconds()

    return len(featureplaces) > 0

  except Exception as e:
    print e
