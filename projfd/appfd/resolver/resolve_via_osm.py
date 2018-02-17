from appfd.models import Place
from django.contrib.gis.geos import Point
import json
from language_detector import detect_language
#import overpass
from overpass import API
from requests import get

def run(names, countries=[]):
    try:
        print("starting resolve_via_osm with:")

        api = API()
        query = "("
        for index, name in enumerate(names):
            if isinstance(name, str):
                name = name.encode("utf-8")
            query += '\nnode["name"="' + name + '"];'
            #language = detect_language(name)
            language = "Arabic" if index == 0 else "English"
            print("language:", language)
            if language == "Arabic":
                query += '\nnode["name:ar"="' + name + '"];'
            elif language == "English":
                query += '\nnode["name:en"="' + name + '"];'
        query += ");"

        features = api.Get(query)['features']

        # filter by country if applicable
        if countries:
            polygons = [place.mpoly for place in Place.objects.filter(admin_level=0, name__in=countries) if place.mpoly]

            filtered_features = []
            for feature in features:
                try:
                    geometry = feature['geometry']
                    if geometry['type'] == "Point":
                        point = Point(feature['geometry']['coordinates'])
                        for polygon in polygons:
                            if polygon.contains(point):
                                filtered_features.append(feature)
                except Exception as e:
                    print("CAUGHT:", e)
            features = filtered_features
              
        print("features:", len(features))

        return features

    except Exception as e:
        print(e)
