from appfd.models import Feature, Order, Place
from collections import Counter
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
import appfd, json, geojson
from os import mkdir
from os.path import isdir, isfile

# this returns a geojson representing the frequency of places mentioned
# it currently only supports countries
# but will expand to lower layers
def run(token):
    print "\nstarting create.frequency_geojson"

    from django.db import connection
    connection.close()

    path_to_geojson = "/home/usrfd/maps/" + token + "/" + token + "_frequency.geojson"
    order = Order.objects.filter(token=token).first()
    print "order:", order
    if order:
        features = Feature.objects.filter(order=order)

        #counters, one for each admin level 0 through 5
        counters = [Counter(),Counter(),Counter(),Counter(),Counter()]

        places_by_id = {}

        #print "features:", features
        for feature in features:

            fp = feature.featureplace_set.filter(correct=True).first()
            if fp: 

                place = fp.place
                #print "place:", place

                # not sure what to do once get to high admin levels like 4 and 5
                for admin_level in range(2):
                    if place.admin_level == admin_level:
                        counters[admin_level][place.id] += feature.count or 1
                        places_by_id[place.id] = place
                    elif not place.admin_level or place.admin_level > admin_level:
                        queryset = Place.objects
                        if place.country_code:
                            queryset = queryset.filter(country_code=place.country_code)
                        admin_polygon = queryset.filter(admin_level=admin_level, mpoly__contains=place.point).first()
                        #print "admin_polygon:", admin_polygon
                        if admin_polygon:
                            counters[admin_level][admin_polygon.id] += feature.count or 1
                            places_by_id[admin_polygon.id] = admin_polygon


        for admin_level, counter in enumerate(counters):
            features = []
            total_count = float(sum(counter.values()))
            for place_id in counter:
                properties = {}
                place = places_by_id[place_id]

                if not place.point and place.mpoly:
                    place.point = place.mpoly.centroid
  
                properties['admin_level'] = admin_level
                properties['geonameid'] = place.geonameid
                properties['latitude'] = place.point.y
                properties['longitude'] = place.point.x
                properties['name'] = place.name
                properties['country_code'] = place.country_code
                properties['count'] = count = counter[place_id]
                properties['frequency'] = float(count) / total_count

                # can probably make this more efficient by not just getting string representing of geometry and then converting back to Python obj
                if place.mpoly:
                    features.append(geojson.Feature(geometry=json.loads(place.mpoly.geojson), properties=properties))

            featureCollection = geojson.FeatureCollection(features)
            
            serialized = geojson.dumps(featureCollection, sort_keys=True)
            with open("/home/usrfd/maps/" + token + "/" + token + "_frequency_" + str(admin_level) + ".geojson", "wb") as f:
                f.write(serialized)
