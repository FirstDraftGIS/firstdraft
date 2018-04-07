from appfd.models import *
from appfd.scripts.ai.lsi.get_topic import run as get_topic
from collections import Counter, defaultdict
from decimal import Decimal
#from geojson import Feature, FeatureCollection, MultiPolygon, Point
from datetime import datetime
from django.db import connection
from django.db.models import Q
import editdistance
from marge import predict as marge_predict 
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

    # randomize order in order to minimize statistic bias
    shuffle(names)

    names = list(set(names))
    try: print("names:", names)
    except UnicodeEncodeError: print("couldn't print statement because non-ascii")

    places = Place.objects.filter(name_normalized__in=normalized_names)

    if end_user_timezone:
        for place in places:
            place.matches_end_user_timezone = str(place.timezone == end_user_timezone)
    else:
        for place in places:
            place.matches_end_user_timezone = place.timezone == "Unknown"

    if admin1codes:
        print("admin1codes:", admin1codes)
        places = [p for p in places if p.admin1_code in admin1codes]
        print("filtered by admin1codes")

    print("filtering out places that don't match admin1 code if there is an admin1 code match")
    for location in locations:
        if 'admin1code' in location:
            name = location['name']
            normalized = normalize(name)
            admin1code = location['admin1code'] 
            if admin1code:
                try:print("name:", name)
                except: pass
                print("admin1code:", admin1code)
                # are there any in places that match
                matches = []
                not_matches = []
                for place in place:
                    if name in place.get_all_names() or normalized in place.get_all_names():
                        if place.admin1_code == admin1code:
                            matches.append(place)
                        else:
                            not_matches.append(place)
                #print "matches:", matches
                #print "not_matches:", not_matches
                if matches:
                    for place in not_matches:
                        places.remove(place)

    number_of_places = len(places)

    if number_of_places == 0:
        return False

    print("places", type(places), len(places))

    # calculate median distance from every other point
    #all_cords = [place.point.coords for place in places]
    
    target_places = defaultdict(list)
    target_coords = defaultdict(list)
    all_coords = []
    for place in places:
        all_coords.append(place.point.coords)
        target_places[place.name_normalized].append(place)
        target_coords[place.name_normalized].append(place.point.coords)

    print("number of target_places:", len(target_places))
    for target, options in list(target_places.items()):
        for i, v in enumerate(median(cdist(target_coords[target], all_coords), axis=1)):
            target_places[target][i].median_distance_from_all_other_points = int(v)
       
        #print "name_topic names are", name_topic.keys() 
        topic_id = name_topic[target]
        #print "topic:", topic_id
        for option in options:
            #print "\toption.topic_id:", option.topic_id
            option.matches_topic = option.topic_id == topic_id

    mode = "local" if order.end_user_timezone else "global"
    
    print("need to choose one for each target based on highest probability")
    for target, options in list(target_places.items()):

        importances = [option.importance for option in options if option.importance]
        print("importances:", importances)
        median_importance = median([importances]) if importances else 0.5
        print("median_importance:", median_importance)

        # convert geoenties to Pandas dataframe
        options_as_dicts = []
        for option in options:
            population = option.population or 0
            option_as_dict = {
                "importance": option.importance or median_importance,
                "has_enwiki_title": 1 if option.enwiki_title else 0,
                "has_population_over_1_million": 1 if population > 1e5 else 0,
                "has_population_over_1_thousand": 1 if population > 1e3 else 0, 
                "has_population_over_1_hundred": 1 if population > 1e2 else 0
            }
            options_as_dicts.append(option_as_dict)
        df = DataFrame(options_as_dicts)
        print("df:", df)
        for index, probability in enumerate(marge_predict.get_probabilities(df)):
            print("MARGE proba:", probability)
            options[index].probability = probability
        
        target_lowered = target.lower()

        country_code = name_country_code.get(target_lowered, None)
        if country_code:
            matches_country_code = [o for o in options if o.country_code == country_code]
            if debug: print("matches_country_code:", matches_country_code)
        else:
            matches_country_code = []

        if country_code and matches_country_code:
            max_probability = max([o.probability for o in matches_country_code])
        else:
            max_probability = max([o.probability for o in options])

        found_correct = False
        for option in options:
            if not found_correct and option.probability == max_probability and (not matches_country_code or option in matches_country_code):
                option.correct = True
                found_correct = True
            else:
                option.correct = False
 
    #Feature, FeaturePlace
    featureplaces = [] 
    for target, options in list(target_places.items()):
        l = name_location[target]
        topic_id = name_topic.get(target, None)
        count = l['count'] if 'count' in l else 1
        correct_option = next(option for option in options if option.correct)
        geometry_used = "Shape" if correct_option.mpoly else "Point"
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
            featureplaces.append(FeaturePlace(confidence=float(option.probability), correct=option.correct, feature=feature, place_id=option.id, sort_order=-1))


    FeaturePlace.objects.bulk_create(featureplaces)

    print("resolved locations for order " + str(order_id))

    print("took:", (datetime.now() - start).total_seconds())

    return len(featureplaces) > 0

  except Exception as e:
    print(e)
