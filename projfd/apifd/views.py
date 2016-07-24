from .scripts.create.frequency_geojson import run as create_frequency_geojson
from appfd.models import Feature, Order, Place
from collections import Counter
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
import appfd, json, geojson
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
def frequency(request, token):
    print "\nstarting frequency"
    print 'request.method', request.method

    path_to_geojson = "/home/usrfd/maps/" + token + "/" + token + "_frequency.geojson"
    if isfile(path_to_geojson):
        print "found", path_to_geojson
        with open(path_to_geojson) as f:
            text = f.read()
        return HttpResponse(text)
    else:
        return HttpResponse(create_frequency_geojson(token))

