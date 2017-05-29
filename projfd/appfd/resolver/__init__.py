#from appfd.models import Feature, Place
from appfd.geoentity import GeoEntity
from appfd.models import *
from appfd.scripts.ai import predict
from appfd.scripts.ai.lsi.get_topic import run as get_topic
from collections import Counter, defaultdict
from decimal import Decimal
#from geojson import Feature, FeatureCollection, MultiPolygon, Point
from datetime import datetime
from django.db import connection
from django.db.models import Q
import editdistance
from multiprocessing import *
from numpy import amin, argmin, mean, median, where
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

# takes in a list of locations and resovles them to features in the database
def resolve_locations(locations, order_id, max_seconds=10, countries=[], admin1codes=[], debug=True):
  try:
    print "starting resolve_locations with", type(locations)
    print "locations = ", len(locations), locations[:5]
    print "countries:", countries
    print "admin1codes:", admin1codes

    start = datetime.now()

  
    order = Order.objects.get(id=order_id)

    name_country = {}
    name_country_code = {}
    name_location = {}
    name_topic = {}
    names = []
    for location in locations:
        #cleaning name a little just to play it safe; sometimes have blank depending on extract method
        name = location['name'] = location['name'].strip()
        #skipping over places with commas and parentheses in them.. because won't find in db anyway... probably need more longterm solution like escape quoting in psql
        if name and not any(char in name for char in [',', ')', '(', '?', "'", '"', "}", "{"]): 
            names.append(name)
            name_location[name] = location
            if location.get('country', None):
                name_country[name] = location['country']
            if location.get('country_code', None):
                name_country_code[name] = location['country_code']
            if "context" in location:
                topic_id = get_topic(location['context'])
                location['topic_id'] = topic_id
                name_topic[name] = topic_id
            else:
                name_topic[name] = None


    number_of_locations = len(locations)

    #print "names", len(names), names[:5]

    # randomize order in order to minimize statistic bias
    shuffle(names)

    names = set(names)
    print "names:", names

    cursor = connection.cursor()

    seconds_left = max_seconds - (datetime.now().replace(tzinfo=UTC) - order.start).total_seconds() 
    print "seconds_left:", seconds_left
    if seconds_left > 60:
        if countries:
            statement = "SELECT * FROM fdgis_resolve_with_countries('{" + ", ".join(names) + "}'::TEXT[], '{" + ", ".join(countries) + "}'::TEXT[], true);"
        else:
            statement = "SELECT * FROM fdgis_resolve('{" + ", ".join(names) + "}'::TEXT[], true);"
    else:
        if countries:
            statement = "SELECT * FROM fdgis_resolve_with_countries('{" + ", ".join(names) + "}'::TEXT[], '{" + ", ".join(countries) + "}'::TEXT[], false);"
        else:
            statement = "SELECT * FROM fdgis_resolve('{" + ", ".join(names) + "}'::TEXT[], false);"



    print "statement:\n", statement
    cursor.execute(statement)
    #print "executed"

    geoentities = []
    for row in cursor.fetchall():
        try:
            geoentities.append(GeoEntity(row))
        except Exception as e:
            print "exception creating geoentity... skipping"
    
    print "created " + str(len(geoentities)) + " geoentities"

    if admin1codes:
        print "admin1codes:", admin1codes
        geoentities = [g for g in geoentities if g.admin1code in admin1codes]
        print "filtered by admin1codes"

    print "filtering out geoentities that don't match admin1 code if there is an admin1 code match"
    for location in locations:
        if 'admin1code' in location:
            name = location['name']
            admin1code = location['admin1code'] 
            if admin1code:
                try:print "name:", name
                except: pass
                print "admin1code:", admin1code
                # are there any in geoentities that match
                matches = []
                not_matches = []
                for geoentity in geoentities:
                    if geoentity.place_name == name or geoentity.alias == name:
                        if geoentity.admin1code == admin1code:
                            matches.append(geoentity)
                        else:
                            not_matches.append(geoentity)
                #print "matches:", matches
                #print "not_matches:", not_matches
                if matches:
                    for geoentity in not_matches:
                        geoentities.remove(geoentity)

    number_of_geoentities = len(geoentities)

    if number_of_geoentities == 0:
        return False

    print "geoentities", type(geoentities), len(geoentities)

    # calculate median distance from every other point
    #all_cords = [geoentity.point.coords for geoentity in geoentities]

    target_geoentities = defaultdict(list)
    target_coords = defaultdict(list)
    all_coords = []
    for geoentity in geoentities:
        all_coords.append(geoentity.point.coords)
        target_geoentities[geoentity.target].append(geoentity)
        target_coords[geoentity.target].append(geoentity.point.coords)

    #number_of_clusters =  max(3, number_of_locations/20)
    number_of_clusters = 3 if len(all_coords) >= 3 else len(all_coords)
    print "number_of_clusters:", number_of_clusters
    #centroids = kmeans(all_coords, number_of_clusters)[0]
    #print "centroids:", centroids
    estimator = KMeans(n_clusters=number_of_clusters)
    #print "all_coords:", all_coords
    estimator.fit(all_coords)
    print "fit estimator"
    labels = estimator.labels_
    cluster_count = Counter()
    for cluster in labels:
        cluster_count[cluster] += 1
    cluster_frequency = {cluster: float(count) / number_of_geoentities for cluster, count in cluster_count.iteritems() }
    for i in range(number_of_geoentities):
        geoentities[i].cluster_frequency = cluster_frequency[labels[i]]
    

    print "number of target_geoentities:", len(target_geoentities)
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

        country_code = name_country_code.get(target, None)
        if country_code:
            matches_country_code = [o for o in options if o.country_code == country_code]
            if debug: print "matches_country_code:", matches_country_code
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
    for target, options in target_geoentities.items():
        l = name_location[target]
        topic_id = name_topic[target] if target in name_topic else None
        count = l['count'] if 'count' in l else 1
        correct_option = next(option for option in options if option.correct)
        geometry_used = "Shape" if correct_option.has_mpoly else "Point"
        feature = Feature.objects.create(count=count, name=target, geometry_used=geometry_used, order_id=order_id, topic_id=topic_id, verified=False)
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
            featureplaces.append(FeaturePlace(confidence=float(option.probability), correct=option.correct, country_rank=option.country_rank, feature=feature, median_distance=option.median_distance_from_all_other_points, place_id=option.place_id, popularity=option.popularity, sort_order=-1))


    FeaturePlace.objects.bulk_create(featureplaces)

    print "resolved locations for order " + str(order_id)

    print "took:", (datetime.now() - start).total_seconds()

    return len(featureplaces) > 0

  except Exception as e:
    print e
