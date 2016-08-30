import appfd, json, geojson
from .scripts.create.frequency_geojson import run as create_frequency_geojson
from appfd.scripts import create_geojson, create_csv, create_shapefiles
from appfd.models import Feature, Order, Place
from collections import Counter
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from multiprocessing import Process
from os import mkdir
from os.path import isdir, isfile


@xframe_options_exempt
def data(request):
    print "starting data"
    print "request.method:", request.method
    if request.method == "POST":
        print "request:", request.POST
        order = Order.objects.get(token=request.POST['token'])
        print "order:", order
        print "Order:", Order
        print "Feature:", Feature
        print "feats:", Feature.objects.all()
        data = []
        for feature in Feature.objects.filter(order=order):
            datum = {
                "admin_level": feature.place.admin_level,
                "admin1_code": feature.place.admin1_code,
                "admin2_code": feature.place.admin2_code,
                "area_sqkm": feature.place.area_sqkm,
                "confidence": feature.confidence,
                "correct": feature.correct,
                "country_code": feature.place.country_code,
                "district_num": feature.place.district_num,
                "end": feature.end,
                "fips": feature.place.fips,
                "geonameid": feature.place.geonameid,
                "name": feature.place.name,
                "start": feature.start,
                "text": feature.text
            }
            data.append(datum)
        return HttpResponse(json.dump(data))
    else:
        return HttpResponse("You have to use post")

# this returns a geojson representing the frequency of places mentioned
# it currently only supports countries
# but will expand to lower layers
@xframe_options_exempt
def frequency(request, token, admin_level):
    print "\nstarting frequency"
    print 'request.method', request.method

    path_to_geojson = "/home/usrfd/maps/" + token + "/" + token + "_frequency_" + str(admin_level) + ".geojson"
    if not isfile(path_to_geojson):
        create_frequency_geojson(token)
    with open(path_to_geojson) as f:
        text = f.read()
    return HttpResponse(text)

def features(request, token):
    print "starting apifd.features with", token

    order = Order.objects.get(token=token)

    list_of_features = []
    for feature in Feature.objects.filter(order_id=order.id):
        d = {}
        if feature.place.admin_level:
            d['admin_level'] = feature.place.admin_level
        d['id'] = feature.id
        d['confidence'] = feature.confidence
        if feature.end:
            d['end_time'] = feature.end.strftime('%y-%m-%d')
        if feature.start:
            d['start_time'] = feature.start.strftime('%y-%m-%d') 
        d['correct'] = feature.correct
        d['country_code'] = feature.place.country_code
        d['geometry_used'] = feature.geometry_used
        d['name'] = feature.place.name
        if feature.place.geonameid:
            d['geonameid'] = feature.place.geonameid
        if feature.place.pcode:
            d['pcode'] = feature.place.pcode
        d['latitude'] = feature.place.point.y
        d['longitude'] = feature.place.point.x
        if feature.text:
            d['text'] = feature.text
        if feature.place.mpoly:
            coords = feature.place.mpoly.coords
            length_of_coords = len(coords)
            if length_of_coords == 1:
                d['polygon'] = coords[0]
            elif length_of_coords > 1:
                d['multipolygon'] = coords
        list_of_features.append(d)

    return HttpResponse(json.dumps({"edited": order.edited, "features": list_of_features}), content_type='application/json')

def mark_feature_incorrect(self, feature_id):
    try:
        print "starting mark_feature_incorrect with feature_id", feature_id
        feature = Feature.objects.get(id=feature_id)
        feature.correct = False
        feature.save()

        token = feature.order.token

        from django.db import connection 
        connection.close()

        Process(target=create_csv.run, args=(token,)).start()
        Process(target=create_geojson.run, args=(token,)).start()
        Process(target=create_shapefiles.run, args=(token,)).start()

        return HttpResponse("done")
    except Exception as e:
        print e

def ready(self, token): 
    try:
        complete = Order.objects.get(token=token).complete
        if complete:
            return HttpResponse("ready")
        else:
            return HttpResponse("nope")
    except Exception as e:
        print e
