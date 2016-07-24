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

    path_to_geojson = "/home/usrfd/maps/" + token + "/" + token + "_frequency.geojson"
    order = Order.objects.filter(token=token).first()
    print "order:", order
    if order:
        features = Feature.objects.filter(order=order)

        countries = set()

        country_codes = Counter() 

        print "features:", features
        for feature in features:
            place = feature.place
            print "place:", place
            if place.admin_level == 0:
                countries.add(place)
            if place.country_code:
                country_codes[place.country_code] += feature.count or 1
            else:
                try:
                    country_code = Place.objects.get(admin_level=0, mpoly__contains=point).country_code
                    country_codes[country_code] += feature.count or 1
                except Exception as e: print e

        features = []
        print "country_codes:", country_codes

        total_count_of_countries = float(sum(country_codes.values()))
        for country_code in country_codes:
            print "\tfor country_code:", country_code
            properties = {}

            place = Place.objects.get(admin_level=0, country_code=country_code)
            properties['geonameid'] = place.geonameid
            properties['name'] = place.name
            properties['country_code'] = country_code
            properties['count'] = count = country_codes[country_code]
            properties['frequency'] = float(count) / total_count_of_countries

            # can probably make this more efficient by not just getting string representing of geometry and then converting back to Python obj
            features.append(geojson.Feature(geometry=json.loads(place.mpoly.geojson), properties=properties))
        featureCollection = geojson.FeatureCollection(features)
            
        serialized = geojson.dumps(featureCollection, sort_keys=True)
        with open("/home/usrfd/maps/" + token + "/" + token + "_frequency.geojson", "wb") as f:
            f.write(serialized)

        return serialized

    else:
        return "We couldn't find an order with that token"

