import appfd, json, geojson
from .scripts.create.frequency_geojson import run as create_frequency_geojson
from appfd.scripts.create import create_csv, create_geojson, create_images, create_pdf, create_shapefiles, create_xypair
from appfd.models import Feature, FeaturePlace, MapStyle, MetaData, MetaDataEntry, Order, Place, Style
from collections import Counter
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.clickjacking import xframe_options_exempt
from multiprocessing import Process
from os import mkdir
from os.path import isdir, isfile
import json

@require_POST
def change_basemap(request):
    try:
        d = json.loads(request.body)
        token = d['token']
        MapStyle.objects.filter(order__token=token).update(basemap_id=d['id'])

        from django.db import connection 
        connection.close()

        for _method in create_geojson.run, create_frequency_geojson, create_shapefiles.run, create_csv.run, create_images.run, create_xypair.run, create_pdf.run:
            Process(target=_method, args=(token,)).start()

        status = "success"
    except Exception as e:
        print "[exception in change_basemap]", e
        status = "failure"

        print "status:", status
    return HttpResponse(json.dumps({"status": status}))

@require_POST
def change_featureplace(request):
    try:
        if request.method == "POST":
            d = json.loads(request.body)
            print "d:", d
            fp = FeaturePlace.objects.get(id=int(d['featureplace_id'])) # converting to int to prevent sql injection
            if "correct" in d:
                fp.correct = d["correct"] == True # checking to prevent sql injection
            fp.save()

            feature = fp.feature
            feature.verified
            feature.save()

            token = feature.order.token

            from django.db import connection 
            connection.close()

            for _method in create_geojson.run, create_frequency_geojson, create_shapefiles.run, create_csv.run, create_images.run, create_xypair.run:
                Process(target=_method, args=(token,)).start()

            return HttpResponse("done")
        else:
            return HttpResponse("You have to use post")
    except Exception as e:
        print e

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

def metadata(request, token):
    print "starting apifd.metadata with", token

    list_of_metadata = []
    for metaData in MetaData.objects.filter(order__token=token):
        list_of_metadata.append(list(MetaDataEntry.objects.filter(metadata=metaData).values()))

    return HttpResponse(json.dumps({"metadata": list_of_metadata}), content_type='application/json')

@require_GET
def features(request, token):
  try:
    print "starting apifd.features with", token

    order = Order.objects.get(token=token)

    list_of_features = []
    for feature in Feature.objects.filter(order_id=order.id):
        feature_id = feature.id
        style = Style.objects.filter(feature_id=feature_id).values("fill", "fillOpacity", "label", "stroke", "strokeOpacity", "strokeWidth").first()
        for fp in feature.featureplace_set.all():

            place = fp.place

            d = {}
            if style:
                d['style'] = style
            if place.admin_level:
                d['admin_level'] = place.admin_level
            d['feature_id'] = feature_id
            d['featureplace_id'] = fp.id
            d['confidence'] = float(fp.confidence)
            if feature.end:
                d['end_time'] = feature.end.strftime('%y-%m-%d')
            if feature.start:
                d['start_time'] = feature.start.strftime('%y-%m-%d') 
            d['correct'] = fp.correct
            if place.country_code:
                d['country_code'] = place.country_code
            d['geometry_used'] = feature.geometry_used
            d['name'] = feature.name
            if place.name != feature.name:
                d['aliases'] = [place.name]
            if place.geonameid:
                d['geonameid'] = place.geonameid
            if place.pcode:
                d['pcode'] = place.pcode
            d['latitude'] = place.point.y
            d['longitude'] = place.point.x
            if feature.text:
                d['text'] = feature.text
            if place.mpoly:
                coords = place.mpoly.coords
                length_of_coords = len(coords)
                if length_of_coords == 1:
                    d['polygon'] = coords[0]
                elif length_of_coords > 1:
                    d['multipolygon'] = coords
            list_of_features.append(d)


    basemap = order.style.basemap
    style = {"basemap_id": basemap.id, "basemap_code": basemap.name}

    return HttpResponse(json.dumps({ "edited": order.edited, "features": list_of_features, "style": style }), content_type='application/json')
  except Exception as e:
    print e

@require_POST
def is_location_in_osm(request):
    try:
        print "starting is_location_in_osm"
        if request.method == "POST":
            if len(request.body.strip()) > 10:
                d = json.loads(request.body)
            elif request.POST:
                d = request.POST

            name = d['name']
            countries = [d['country']] if 'country' in d else []

            if resolve_via_osm(names=[name], countries=countries):
                answer = True
            else:
                answer = False
            return HttpResponse(json.dumps({"answer": answer}), content_type='application/json')
        else:
            return HttpResponse("Use POST, please.", content_type='application/json')
 
    except Exception as e:
        print e

@require_GET
def ready(self, token): 
    try:
        complete = Order.objects.get(token=token).complete
        if complete:
            return HttpResponse("ready")
        else:
            return HttpResponse("nope")
    except Exception as e:
        print e
