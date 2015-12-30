from appfd.models import *
from collections import Counter
from geojson import Feature, FeatureCollection, MultiPolygon, Point
from django.db.models import Q
from multiprocessing import *
from timeit import default_timer
from time import sleep
from threading import *

# takes in a location as input text and returns the location
def resolve(text):
    print "starting resolve with text", text

    if text:
        #should give preference to citiesd
        # also locational culstering... expectation maximization algorithm??, number of clusters is dynamic...
        # order by admin level, so have higher chance of getting the country of Spain than some city called Spain
        locations = Place.objects.filter(name=text).order_by('admin_level','pcode','-population')
        count = locations.count()

        if count == 0:
            print "count is 0"
            locations = Place.objects.filter(aliases__alias=text).order_by('admin_level','pcode','-population')
            count = locations.count()
            if count == 0:
                print "count is still 0"
                locations = list(Place.objects.raw("SELECT * FROM appfd_place WHERE levenshtein_less_equal('" + text + "', name, 1) = 1 ORDER BY admin_level, pcode, -1 * population;"))
                count = len(locations)
                if count == 0:
                    print "Wow! still can't find " + text + ". We're going to drop the barrier to 2 levenshtein distances"
                    locations = list(Place.objects.raw("SELECT * FROM appfd_place WHERE levenshtein_less_equal('" + text + "', name, 2) = 2 ORDER BY admin_level, pcode, -1 * population;"))
                    count = len(locations)
                    if count == 0:
                        print "give up on ", text
                    elif count == 1:
                        return locations[0]
                    else:
                        return locations[0]
                elif count == 1:
                    return locations[0]
                else:
                    print "count > 1 with levenshtein distance 1, just return first element returned"
            elif count == 1:
                print "count is 1"
                return locations[0]
            else:
                print "count > 0"
                return locations[0]

        elif count == 1:
            print "count is 1 so returning", locations[0]
            return locations[0]
        else: # count > 1
            print "count is greater than 1"
            print "    locations are", locations
            for location in locations:
                print "\tlocation.admin_level = ", location.admin_level
                print "\tlocation.point = ", location.point
                print "\tlocation.pcode = ", location.pcode
                print "\tlocation.geonameid = ", location.geonameid
            return locations[0]
            # should also do locational clustering and if any points are more than two standard deviations away, look for other example

# takes in a location dictionary
# returns a feature
def location_to_feature(location):

    properties = location
    place = resolve(location['name'])
    if place:
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
            print "set country_code to ", country_code

        if 'date' in location:
            date = location['date']
            if date:
                location['start_time'] = location['end_time'] = location['date'] = date.strftime('%y-%m-%d')
                location['date_pretty'] = date.strftime('%m/%d/%y')
        feature = Feature(geometry=geometry, properties=properties)
        return feature

# takes in a list of locaitons, resolve them and return features
def resolve_locations(locations):

    print "starting resolve_locations"
    start = default_timer()

    features = []

    # filter out locations with names shorter than or equal to 3 characters
    # it's more likely they're errors
    locations = [location for location in locations if len(location['name']) > 3]

    # should also have a list of known non-locations that can filter by
    # hmmm. nvm.. that really should just be in the location-extractor, obvious stuff like calendar months that follow from and to

    for location in locations:
        feature = location_to_feature(location)
        if feature:
            features.append(feature)

    print "features final are", len(features)
    # cluster and clean by country code
    # basically if 90% of the features are in one country
    # then we assume that any features found in another country are a mistake
    # we just remove the mistakes, but in the future, we should make it
    # so we just try to resolve again
    country_codes = [f['properties']['country_code'] for f in features]
    country_code_counter = Counter(country_codes)
    most_common_country_code, most_common_country_code_count = Counter(country_codes).most_common(1)[0]
    if float(most_common_country_code_count) / len(country_codes) > 0.8:
        features = [f for f in features if f['properties']['country_code'] == most_common_country_code]


    print "\n\nFINISHING with time", start - default_timer()

    return features

def run(text=None):
    print "running resolve with ", text
    print "resolved", resolve(text=text)
