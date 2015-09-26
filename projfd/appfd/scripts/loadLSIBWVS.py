from appfd.models import *
from django.contrib.gis.gdal import DataSource
#from django.contrib.gis.gdal.geometries import Polygon
from django.contrib.gis.geos import MultiPolygon, Polygon
import os, urllib, zipfile
from urllib import urlretrieve
from bnlp import trim_location
#wget 'http://geonode.state.gov/geoserver/wfs?format_options=charset%3AUTF-8&typename=geonode%3AAfricaAmericas_LSIB_Polygons_Simplified_2015&outputFormat=SHAPE-ZIP&version=1.0.0&service=WFS&request=GetFeature' -O 'AFRICA_AMERICAS.zip'

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
            name = trim_location(feature.get("CNTRY_NAME"))
            #print feature.fields
            #break
            print 'name is', name
            #country_code = feature.get("CNTRY_CODE")
            country_code = feature.get("iso_alpha2")
            qs = Place.objects.filter(country_code=country_code, admin_level=0)
            count = qs.count()
            if count == 0:
                unfound.append((name,country_code))
                #qs = Place.objects.filter(name__startswith=name)
            #count = qs.count()
            #print "count for namestartswith", name, "is", count
            elif count == 1:
                found.append((name,country_code)) 
                place = qs[0]
            #place.mpoly = MultiPolygon([feature.geom])
                geom = feature.geom.geos
                if isinstance(geom, Polygon):
                    place.mpoly = MultiPolygon([geom])
                elif isinstance(geom, MultiPolygon):
                    place.mpoly = geom
                else:
                    print "name is", name
                place.save()
            elif count > 1:
                print "more than 1", name, country_code
                found.append((name,country_code))

    print "found = ", found
    print "\n\n"
    print "unfound = ", unfound
   
