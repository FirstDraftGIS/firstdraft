from geojson import dumps, FeatureCollection, MultiPolygon, Point, Polygon, GeometryCollection
from os import mkdir
from os.path import isdir, join
from urllib.parse import quote

from appfd.models import FeaturePlace, Order
from geojson import Feature as gFeature
from projfd.additional_settings.firstdraft import MAPS_DIRECTORY, PUBLIC_BASE_URL

def run(key):
    print("starting create_geojson.run with key " + key)

    from django.db import connection
    connection.close()

    features = []
    for fp in FeaturePlace.objects.filter(feature__order__token=key, correct=True).order_by("-place__admin_level"):

            properties = {}

            feature = fp.feature

            if feature.end:
                properties['end_time'] = feature.end.strftime('%y-%m-%d')

            if feature.start:
                properties['start_time'] = feature.start.strftime('%y-%m-%d')

            properties['confidence'] = float(fp.confidence)
            place = fp.place
            properties['admin_level'] = place.admin_level
            properties['admin1_code'] = place.admin1_code
            properties['country_code'] = place.country_code
            try:
                importance = place.wikipedia.importance
            except:
                importance = 0
            properties['importance'] = importance
            properties['name'] = place.name
            properties['geonames_id'] = place.geonames_id
            properties['pcode'] = place.pcode
            properties['timezone'] = place.timezone
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

    directory = join(MAPS_DIRECTORY, key)
    if not isdir(directory):
        mkdir(directory)

    serialized = dumps(featureCollection, sort_keys=True)
    with open(join(directory, key + ".geojson"), "w") as f:
        f.write(serialized)


    print("I finished running create_geojson.  You can view the map here:")
    url = PUBLIC_BASE_URL + "/api/orders/" + key + "/maps/geojson"
    quoted = quote(url)
    print("http://geojson.io/#data=data:text/x-url," + quoted)