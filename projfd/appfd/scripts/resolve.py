from appfd.models import *
from collections import Counter
from geojson import Feature, FeatureCollection, MultiPolygon, Point
from django.db.models import Q
from multiprocessing import *
from random import shuffle
from super_python import *
from sys import exit
from timeit import default_timer
from time import sleep
from threading import *

# takes in a list of locations and resovles them to features in the database
def resolve_locations(locations):
    p("starting resolve_locations with", type(locations))
    p("locations = ", len(locations), locations[:5])

    #defaults
    most_common_country_code = None
    second_most_common_country_code = None
    country_code = None


    list_of_names_of_locations = [location['name'] for location in locations]
    p("list_of_names_of_locations", len(list_of_names_of_locations), list_of_names_of_locations[:5])

    shuffle(list_of_names_of_locations)
    
    # convert to set because we only want uniques
    list_of_names_of_locations = list(set(list_of_names_of_locations))

    sample = list_of_names_of_locations[:20]
    p("sample is", sample)

    places = Place.objects.filter(name__in=sample).order_by("name","admin_level","pcode","-population").distinct("name")
    if places.count() == 0:
        sample = list_of_names_of_locations[:100]
        places = Place.objects.filter(name__in=sample).order_by("name","admin_level","pcode","-population").distinct("name")
        
    if places.count() > 0:
        p("places are", places)
        p("x is", [place.country_code for place in places])
        list_of_most_common_country_codes = Counter([place.country_code for place in places]).most_common(2)
        most_common_country_code, most_common_count = list_of_most_common_country_codes[0]
        second_most_common_country_code, second_most_common_count = list_of_most_common_country_codes[0]
        most_common_frequency = float(most_common_count) / places.count()
        p("most_common_country_code = ", most_common_country_code)
        p("most_common_count = ", most_common_count)
        if most_common_country_code and most_common_frequency >= 0.5:
            country_code = most_common_country_code

    p("country_code = ", country_code)
    d = {}

    base = Place.objects.order_by("name","admin_level","pcode","-population")
    # if already know country code
    if country_code:
        for place in base.filter(country_code=country_code).filter(name__in=list_of_names_of_locations).distinct('name'):
            d[place.name] = {'confidence': 'high', 'place': place}
    else:
        # even if we don't get the same country code for everything
        # we still bias are location resolution by the most commonly mentioned country
        # this helps avoid matching locations in far away countries that happen to share the same name
        places = list(base.filter(name__in=list_of_names_of_locations))
        #print "\nplaces =", places
        names = set([place.name for place in places])
        #print "\nnames =", names
        for name in names:
            #print "\nname = ", name
            places_matching_name = [place for place in places if place.name == name]
            #print "\nplaces_matching_name = ", places_matching_name
            places_matching_country_code = [place for place in places_matching_name if place.country_code == most_common_country_code] or [place for place in places_matching_name if place.country_code == second_most_common_country_code]
            if places_matching_country_code:
                place = places_matching_country_code[0]
            else:
                place = places_matching_name[0]
            d[name] = {'confidence': 'high', 'place': place}

    missing = [name_of_location for name_of_location in list_of_names_of_locations if name_of_location not in d] 
    p("missing = ", len(missing), missing[:5])
    p("after alias", d)
    if missing:
        for place in base.filter(aliases__alias__in=missing):
            p("place via alias is", place.name)
            d[place.name] = {'confidence': 'medium', 'place': place}

        if country_code:
            missing = [name_of_location for name_of_location in list_of_names_of_locations if name_of_location not in d] 
            p("missing = ", len(missing), missing[:5])
            for missing_place in missing:
                matched = list(Place.objects.raw("""
                    WITH place_ldist as (
                        SELECT *, levenshtein_less_equal('""" + missing_place + """', name, 2) as ldistance
                        FROM appfd_place
                        WHERE country_code = '""" + country_code + """'
                    )
                    SELECT * FROM place_ldist WHERE ldistance <= 2 ORDER BY ldistance, admin_level, pcode, -1 * population;
                """))
                if matched:
                    p("missing_place is", missing_place)
                    d[missing_place] = {'confidence': 'low', 'place': matched[0]}

    p("d is", d)
    p("found ", len(d.keys()), "places")

    features = []
    for location in locations:
        name = location['name']
        if name in d:
            properties = location
            d_name = d[name]
            place = d_name['place']
            properties['name'] = place.name
            properties['confidence'] = d_name['confidence']
            properties['geonameid'] = place.geonameid

            pcode = place.pcode
            if pcode:
                properties['pcode'] = pcode

            point = place.point
            geometry = Point((point.x, point.y))

            country_code = place.country_code
            if country_code:
                properties['country_code'] = country_code
            else:
                properties['country_code'] = country_code = Place.objects.get(admin_level=0, mpoly__contains=point).country_code
                place.update({"country_code": country_code})
                p("set country_code to ", country_code)

            if 'date' in location:
                date = location['date']
                if date:
                    location['start_time'] = location['end_time'] = location['date'] = date.strftime('%y-%m-%d')
                    location['date_pretty'] = date.strftime('%m/%d/%y')
            feature = Feature(geometry=geometry, properties=properties)
 
            if feature:
                features.append(feature)

    p("features final are", len(features))

    return features
