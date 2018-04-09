from appfd.models import *
from appfd.scripts.ai.lsi.get_topic import run as get_topic
from collections import Counter, defaultdict
from decimal import Decimal
#from geojson import Feature, FeatureCollection, MultiPolygon, Point
from datetime import datetime
from django.db import connection
from django.db.models import Q
import editdistance
from itertools import groupby
from marge import resolver as marge_resolver
from marge import utils as marge_utils
from multiprocessing import *
from numpy import amin, argmin, mean, median, where
from pandas import DataFrame
from random import shuffle
#from pydash.collections import pluck
from pytz import UTC
from scipy.cluster.vq import kmeans
from scipy.spatial.distance import cdist
from sklearn.cluster import KMeans
from super_python import *
from sys import exit
from timeit import default_timer
from time import sleep
from unidecode import unidecode

def normalize(name):
    lowered = name.lower()
    decoded = unidecode(lowered)
    if len(decoded) > 3:
        return decoded
    else:
        return lowered

def group_into_dict(items, category):
    return dict([(i, list(g)) for i, g in groupby(items, lambda i: i[category])])

def copy_prop(items, from_prop, to_prop):
    for item in items:
        item[to_prop] = item[from_prop]
    return items

# takes in a list of locations and resovles them to features in the database
def resolve_locations(locations, order_id, max_seconds=10, countries=[], admin1codes=[], debug=True, end_user_timezone=None, case_insensitive=None):
  try:
    print("starting resolve_locations with", type(locations))
    print(""*4, "locations = ", len(locations), locations[:5])
    print(""*4, "countries:", countries)
    print(""*4, "admin1codes:", admin1codes)
    print(""*4, "end_user_timezone:", end_user_timezone)
    print(""*4, "case_insensitive:", case_insensitive)

    start = datetime.now()

  
    order = Order.objects.get(id=order_id)

    # make more resilient to unidecode

    name_country = {}
    name_country_code = {}
    name_location = {}
    name_topic = {}
    names = []
    normalized_names = set()
    for location in locations:
        #cleaning name a little just to play it safe; sometimes have blank depending on extract method
        name = location['name'] = location['name'].strip()
        try: print("name:", name)
        except Exception as e: pass
        #skipping over places with commas and parentheses in them.. because won't find in db anyway... probably need more longterm solution like escape quoting in psql
        if name and not any(char in name for char in [',', ')', '(', '?', "'", '"', "}", "{"]): 
            names.append(name)
            normalized = normalize(name)
            normalized_names.add(normalized)
            name_location[normalized] = location
            if location.get('country', None):
                name_country[normalized] = location['country']
            if location.get('country_code', None):
                name_country_code[normalized] = location['country_code']
            if "context" in location:
                topic_id = get_topic(location['context'])
                location['topic_id'] = topic_id
                name_topic[normalized] = topic_id
            else:
                name_topic[normalized] = None


    number_of_locations = len(locations)
    print("number_of_locations:", number_of_locations) 

    #print "names", len(names), names[:5]

    # randomize order in order to minimize statistical bias
    shuffle(names)

    names = list(set(names))
    try: print("names:", names)
    except UnicodeEncodeError: print("couldn't print statement because non-ascii")

    places = Place.objects.filter(name_normalized__in=normalized_names).values()

    number_of_places = len(places)

    if number_of_places == 0:
        return False

    print("places", type(places), len(places))

    copy_prop(places, "name_normalized", "feature_id")

    print("set places", len(places))
    places = marge_utils.to_dicts(marge_resolver.resolve(places))
    print("MARGE resolved:", len(places))

    maxes = marge_utils.max_by_group(places, "probability", "feature_id")
    print("maxes:", maxes)
    
    for option in places:
        fid = option["feature_id"]
        prob = option["probability"]
        option["correct"] = prob == maxes[fid]
    print("resolver SET CORRECT")
 
    # recomposing target places
    target_places = group_into_dict(places, "name_normalized")
    print("recomposed:", list(target_places.keys()))
 
    #Feature, FeaturePlace
    featureplaces = [] 
    for target, options in list(target_places.items()):
        print("target:", target)
        print("\toptions:", options)
        l = name_location[target]
        topic_id = name_topic.get(target, None)
        count = l['count'] if 'count' in l else 1
        correct_option = next(option for option in options if option["correct"])
        geometry_used = "Shape" if correct_option["mpoly"] else "Point"
        feature = Feature.objects.create(count=count, name=l["name"], geometry_used=geometry_used, order_id=order_id, topic_id=topic_id, verified=False)
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
            featureplaces.append(FeaturePlace(confidence=option["probability"], correct=bool(option["correct"]), feature=feature, place_id=option["id"], sort_order=-1))

    FeaturePlace.objects.bulk_create(featureplaces)

    print("resolved locations for order " + str(order_id))

    print("took:", (datetime.now() - start).total_seconds())

    return len(featureplaces) > 0

  except Exception as e:
    print(e)
