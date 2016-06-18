from appfd.models import *
from django.contrib.gis.gdal import DataSource
#from django.contrib.gis.gdal.geometries import Polygon
from django.contrib.gis.geos import MultiPolygon, Polygon
import os, urllib, zipfile
from urllib import urlretrieve
from bnlp import trim_location

def run():

    if not os.path.isfile('/tmp/AFRICAAMERICAS.zip'):
        urlretrieve('http://geonode.state.gov/geoserver/wfs?format_options=charset%3AUTF-8&typename=geonode%3AAfricaAmericas_LSIB_Polygons_Simplified_2015&outputFormat=SHAPE-ZIP&version=1.0.0&service=WFS&request=GetFeature', '/tmp/AFRICAAMERICAS.zip')
        with zipfile.ZipFile('/tmp/AFRICAAMERICAS.zip', "r") as z:
            z.extractall('/tmp/')

    if not os.path.isfile('/tmp/EurasiaOceania.zip'):
        urlretrieve('http://geonode.state.gov/geoserver/wfs?format_options=charset%3AUTF-8&typename=geonode%3AEurasiaOceania_LSIB_Polygons_Simplified_2015&outputFormat=SHAPE-ZIP&version=1.0.0&service=WFS&request=GetFeature', '/tmp/EurasiaOceania.zip')
        with zipfile.ZipFile('/tmp/EurasiaOceania.zip', "r") as z:
            z.extractall('/tmp/')


    countries = Place.objects.filter(admin_level=0)

    found = []
    unfound = []
    for path_to_shp in ('/tmp/AfricaAmericas_LSIB_Polygons_Simplified_2015.shp', '/tmp/EurasiaOceania_LSIB_Polygons_Simplified_2015.shp'):
        ds = DataSource(path_to_shp)
        print "ds is", ds
        for feature in ds[0]:
            place = None
            name = trim_location(feature.get("CNTRY_NAME"))
            #country_code = feature.get("CNTRY_CODE")
            country_code = feature.get("iso_alpha2")
            qs = Place.objects.filter(country_code=country_code, admin_level=0)
            count = qs.count()
            if count == 0:
                qs = Place.objects.filter(admin_level=0, name__startswith=name)
                count = qs.count()
                if count == 0:
                    qs = Place.objects.filter(name__startswith=name)
                    count = qs.count()
                    if count == 0:
                        unfound.append((name,country_code))
                    elif count == 1:
                        #maybe add something in later that checks if distance from poly to point is sane
                        found.append((name,country_code)) 
                        place = qs[0]
                    else:
			unfound.append((name,country_code))
                elif count == 1:
                    place = qs[0]
		    found.append((name,country_code))
                else:
		    unfound.append((name,country_code))

            elif count == 1:
                found.append((name,country_code)) 
                place = qs[0]
            else:
                found.append((name,country_code))

            if place:
                geom = feature.geom.geos
                if isinstance(geom, Polygon):
                    place.mpoly = MultiPolygon([geom])
                elif isinstance(geom, MultiPolygon):
                    place.mpoly = geom
                place.save()
                #print "saved new polygon to ", place
 
    print "unfound = ", unfound
   
