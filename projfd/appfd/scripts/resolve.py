#from appfd.models import Feature, Place
from appfd.models import *
from appfd.scripts.ai import predict
from appfd.scripts.ai.lsi.get_topic import run as get_topic
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
        self.country_rank = row[3] or 999
        self.target, self.edit_distance = row[4].split("--")
        self.edit_distance = int(self.edit_distance)
        self.place_name = row[5]
        self.alias = row[6]
        self.population = int(row[7] or 0)
        self.point = GEOSGeometry(row[8])
        topic_id = row[9]
        self.topic_id = int(topic_id) if topic_id else None
        self.has_mpoly = row[10] == "True"
        self.has_pcode = row[11] == "True"

# takes in a list of locations and resovles them to features in the database
def resolve_locations(locations, order_id, max_seconds=86400):
  try:
    print "starting resolve_locations with", type(locations)
    print "locations = ", len(locations), locations[:5]

    start = datetime.now()

    name_location = {}
    name_topic = {}
    names = []
    for location in locations:
        name = location['name']
        if "," not in name: #skipping over places with commas in them.. because won't find in db anyway... probably need more longterm solution like escape quoting in psql
            names.append(name)
            name_location[name] = location
            if "context" in location:
                topic_id = get_topic(location['context'])
                location['topic_id'] = topic_id
                name_topic[name] = topic_id
            else:
                name_topic[name] = None

    #print "names", len(names), names[:5]

    # randomize order in order to minimize statistic bias
    shuffle(names)

    names = set(names)

    cursor = connection.cursor()

    statement = "SELECT * FROM fdgis_resolve('{" + ", ".join(names) + "}'::TEXT[]);"
    #print statement
    cursor.execute(statement)
    #print "executed"

    geoentities = [GeoEntity(row) for row in cursor.fetchall()]

    #print "geoentities", type(geoentities), len(geoentities)

    # calculate median distance from every other point
    #all_cords = [geoentity.point.coords for geoentity in geoentities]

    target_geoentities = defaultdict(list)
    target_coords = defaultdict(list)
    all_coords = []
    for geoentity in geoentities:
        all_coords.append(geoentity.point.coords)
        target_geoentities[geoentity.target].append(geoentity)
        target_coords[geoentity.target].append(geoentity.point.coords)

    #print "target_geoentities:", len(target_geoentities)
    for target, options in target_geoentities.items():
        #print "target:", target
        for i, v in enumerate(median(cdist(target_coords[target], all_coords), axis=1)):
            target_geoentities[target][i].median_distance_from_all_other_points = int(v)
       
        #print "name_topic names are", name_topic.keys() 
        topic_id = name_topic[target]
        #print "topic:", topic_id
        for option in options:
            #print "\toption.topic_id:", option.topic_id
            option.matches_topic = option.topic_id == topic_id

    print "add probability to each geoentity"
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
        l = name_location[target]
        topic_id = name_topic[target] if target in name_topic else None
        feature = Feature.objects.create(count=l['count'], name=target, geometry_used="Point", order_id=order_id, topic_id=topic_id, verified=False) 
        need_to_save = False
        if "context" in l:
            feature.text = l['context']
            need_to_save = True
        if "date" in l:
            feature.end = l['date']
            feature.start = l['date']
            need_to_save = True
        if need_to_save:
            feature.save()
        for option in options:
            featureplaces.append(FeaturePlace(confidence=float(option.probability), correct=option.correct, country_rank=option.country_rank, feature=feature, median_distance=option.median_distance_from_all_other_points, place_id=option.place_id))

    FeaturePlace.objects.bulk_create(featureplaces)

    print "resolved locations for order " + str(order_id)

    print "took:", (datetime.now() - start).total_seconds()

    return len(featureplaces) > 0

  except Exception as e:
    print e
