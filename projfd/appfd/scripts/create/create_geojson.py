from appfd.models import Feature as mFeature
from appfd.models import Order
from geojson import Feature as gFeature
from geojson import dumps, FeatureCollection, MultiPolygon, Point, Polygon, GeometryCollection
from os import mkdir
from os.path import isdir

def run(key):
    print "starting create_geojson with key " + key

    from django.db import connection
    connection.close()

    features = []
    for feature in mFeature.objects.filter(order__token=key):

        fp = feature.featureplace_set.filter(correct=True).first()
        if fp:

            properties = {}

            if feature.end:
                properties['end_time'] = feature.end.strftime('%y-%m-%d')

            if feature.start:
                properties['start_time'] = feature.start.strftime('%y-%m-%d')

            properties['confidence'] = float(fp.confidence)
            place = fp.place
            properties['country_code'] = place.country_code
            properties['name'] = place.name
            properties['geonameid'] = place.geonameid
            properties['pcode'] = place.pcode
            point = Point((place.point.x, place.point.y))
            geometries = [point]
            if place.mpoly:
                coords = place.mpoly.coords
                length_of_coords = len(coords)
                if length_of_coords == 1:
                    geometries.append(Polygon(coords[0]))
                elif length_of_coords > 1:
                    geometries.append(MultiPolygon(coords))
            gc = GeometryCollection(geometries)
            features.append(gFeature(geometry=gc, properties=properties))
    featureCollection = FeatureCollection(features)

    directory = "/home/usrfd/maps/" + key + "/"
    if not isdir(directory):
        mkdir(directory)

    serialized = dumps(featureCollection, sort_keys=True)
    with open(directory + key + ".geojson", "wb") as f:
        f.write(serialized)
