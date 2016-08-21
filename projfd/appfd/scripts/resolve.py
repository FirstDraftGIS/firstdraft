#from appfd.models import Feature, Place
from appfd.models import *
from collections import Counter, defaultdict
#from geojson import Feature, FeatureCollection, MultiPolygon, Point
from datetime import datetime
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
from threading import *

def number_of_keys(d):
    return len(d)

def uniquify(iterable):
    if isinstance(iterable, list):
        return list(set(iterable))

# converts a queryset into a dict keyed by an attribute
def queryset_to_dict(queryset, attribute):
    d = {}
    name_of_item = queryset.model.__name__.lower()
    for item in queryset:
        value = item.__getattribute__(attribute)
        if value in d:
            d[value].append({name_of_item: item})
        else:
            d[value] = [{name_of_item: item}]
    return d

def filter_by_attribute_value(iterable, name, value):
    result = [item for item in iterable if item.__getattribute__(name) == value]
    return result if result else iterable

def filter_dictionary_by_attribute_value(d, attribute, value):
    for name in d:
        options = d[name]
        #print "options:", options
        filtered_options = [option for option in options if option['place'].__getattribute__(attribute) == value]
        d[name] = filtered_options if len(filtered_options) > 0 else options
    return d

# removes all other possibilities if it has this attribute
def filter_dictionary_by_attribute(d, attribute):
    for name in d:
        options = d[name]
        #print "options:", options
        filtered_options = [option for option in options if option['place'].__getattribute__(attribute)]
        d[name] = filtered_options if len(filtered_options) > 0 else options
    return d


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
 

# takes in a list of locations and resovles them to features in the database
def resolve_locations(locations, max_seconds=86400):
  try:
    print "starting resolve_locations with", type(locations)
    print "locations = ", len(locations), locations[:5]

    #defaults
    most_common_country_code = None
    second_most_common_country_code = None
    country_code = None

    list_of_found_places = []

    list_of_names_of_locations = [location['name'] for location in locations]
    print "list_of_names_of_locations", len(list_of_names_of_locations), list_of_names_of_locations[:5]

    # randomize order in order to minimize statistic bias
    shuffle(list_of_names_of_locations)

    list_of_names_of_locations = uniquify(list_of_names_of_locations)

    places = Place.objects.filter(name__in=list_of_names_of_locations[:500])
    print "places:", len(places)
    if places:
        dict_of_places_by_name = queryset_to_dict(places, "name")
        #if number_of_keys(dict_of_places_by_name) < 10:
        #    places = Place.objects.filter(name__in=list_of_names_of_locations[:100])
        #    dict_of_places_by_name = queryset_to_dict(places, "name")

        # should do some filtering, so if have pcode or higher admin_level do that one or maybe if have both pops and 1 has higher population?
        filter_dictionary_by_attribute(dict_of_places_by_name, "pcode")

        places = filter_dict_by_distance(dict_of_places_by_name)

    number_of_places = len(places)

    if number_of_places > 0:
        print "country codes are", [place.country_code for place in places]
        list_of_most_common_country_codes = Counter([place.country_code for place in places]).most_common(2)
        most_common_country_code, most_common_count = list_of_most_common_country_codes[0]
        second_most_common_country_code, second_most_common_count = list_of_most_common_country_codes[0]
        most_common_frequency = float(most_common_count) / number_of_places
        print("most_common_country_code:", most_common_country_code)
        print("most_common_count:", most_common_count)
        # see if more than one country name in list of places, beause if yes, then don't set country_code
        if most_common_country_code and most_common_frequency >= 0.75:

            # don't set the country_code if have more than one country mentioned in text
            # it'll still use the most and second most common country codes to bias the following passes
            # errrr or maybe should set it but make exception for country names
            # like an article that is about events in a country and how other countries are responding to it
            countries = set([most_common_country_code] + uniquify([place.country_code for place in places if place.admin_level == 0]))
            print "countries:", countries
            if len(countries) <= 1:
                country_code = most_common_country_code

    print "country_code:", country_code
    d = {}
    # if already know country code
    if country_code:
        dict_of_places = queryset_to_dict(Place.objects.filter(country_code=country_code).filter(name__in=list_of_names_of_locations), "name")
        #"admin_level", population)
        # within country, not sure if filtering by admin_level makes sense
        dict_of_places = filter_dictionary_by_attribute(dict_of_places, "pcode")
        list_of_found_places = filter_dict_by_distance(dict_of_places)

    else:
        #"name","admin_level","pcode","-population")
        # even if we don't get the same country code for everything
        # we still bias are location resolution by the most commonly mentioned country
        # this helps avoid matching locations in far away countries that happen to share the same name
        dict_of_places = queryset_to_dict(Place.objects.filter(name__in=list_of_names_of_locations), "name")
        dict_of_places = filter_dictionary_by_attribute_value(dict_of_places, "admin_level", 0)
        if most_common_country_code:
            dict_of_places = filter_dictionary_by_attribute_value(dict_of_places, "country_code", most_common_country_code)
        if second_most_common_country_code:
            dict_of_places = filter_dictionary_by_attribute_value(dict_of_places, "country_code", second_most_common_country_code)
        list_of_found_places = filter_dict_by_distance(dict_of_places)

    # add places found in first pass
    for place in list_of_found_places:
        d[place.name] = {"confidence": "high", "place": place}

    print "\n\n\nd:", d
    list_of_names_of_found_places = [place.name for place in list_of_found_places]
    missing = [name_of_location for name_of_location in list_of_names_of_locations if name_of_location not in list_of_names_of_found_places]
    print "missing ", len(missing), missing[:5]
    if missing:

        # VIA ALIAS
        print "NOW, RESOLVING PLACES VIA ALIAS"
        # this code adds the alias attribute to the place which stores alias used to find it
        places_found_via_alias = Place.objects.raw("SELECT *, appfd_alias.alias as alias FROM appfd_place INNER JOIN appfd_aliasplace on (appfd_place.id = appfd_aliasplace.place_id) INNER JOIN appfd_alias ON (appfd_aliasplace.alias_id = appfd_alias.id) WHERE appfd_alias.alias IN (" + ",".join(["'"+p+"'" for p in missing]) + ");")
        print "len(list_of_places_found_via_alias):", len([p for p in places_found_via_alias])
        dict_of_places = queryset_to_dict(places_found_via_alias, "name")
        print "dict_of_places", dict_of_places
        if country_code:
            dict_of_places = filter_dictionary_by_attribute_value(dict_of_places, "country_code", country_code)
        if most_common_country_code:
            dict_of_places = filter_dictionary_by_attribute_value(dict_of_places, "country_code", most_common_country_code)
        if second_most_common_country_code:
            dict_of_places = filter_dictionary_by_attribute_value(dict_of_places, "country_code", second_most_common_country_code)
        list_of_places_found_via_alias = filter_dict_by_distance(dict_of_places)
        list_of_found_places += list_of_places_found_via_alias

        # add places found in pass via alias
        for place in list_of_places_found_via_alias:
            d[place.name] = {'confidence': 'medium', 'place': place}

        list_of_names_of_found_places = [place.name for place in list_of_found_places]
        missing = [name_of_location for name_of_location in list_of_names_of_locations if name_of_location not in list_of_names_of_found_places]
        print "missing after looking at aliases:", len(missing), missing[:10]

        # really should be getting how much time has passed so far and then running timeout catching on how much time can allocate to this
        if country_code or most_common_country_code:
            number_missing = len(missing)
            print "will look for " + str(number_missing) + " places via levenshtein distance"
            count = 0
            for missing_place in missing:
                count += 1
                if count % 10 == 0:
                    print str(float(count) * 100 / number_missing), "% done"

                if max_seconds and (datetime.now() - start).total_seconds() < max_seconds - 5:
                    print "about to run out of time, so stop searching via Levenshtein distance"
                    break

                matched = list(Place.objects.raw("""
                    WITH place_ldist as (
                        SELECT *, levenshtein_less_equal('""" + missing_place + """', name, 2) as ldistance
                        FROM appfd_place
                        WHERE country_code = '""" + (country_code or most_common_country_code) + """'
                    )
                    SELECT * FROM place_ldist WHERE ldistance <= 2 ORDER BY ldistance, admin_level, pcode, -1 * population;
                """))
                if matched:
                    place = matched[0]
                    if float(editdistance.eval(place.name, missing_place)) / mean([len(place.name), len(missing_place)]) < 0.5:
                        print place, "found via levenstein distance for", missing_place
                        place.alias = missing_place # adds alias to the place object, use this later
                        list_of_found_places.append(place)
                        d[place.name] = {'confidence': 'low', 'place': place}
    
    print "list_of_found_places:", list_of_found_places

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

        if not place.country_code:
            try:
                country_code = Place.objects.get(admin_level=0, mpoly__contains=place.point).country_code
                place.update({"country_code": country_code})
                p("set country_code to ", country_code)
            except Exception as e:
                print e
                # should probably put some logic in here, so if don't get country code try to find closest country or get country within 50 miles???

        if "date" in location:
            feature.end = location['date']
            feature.start = location['date']
        if "context" in location:
            feature.text = location['context'][:1000]
        features.append(feature)

    print "features final are", len(features)

    return features

  except Exception as e:
    print e
