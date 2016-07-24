import csv, subprocess
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import Point
from django.contrib.gis.geos import fromstr
from django.contrib.gis.geos import Point, WKBWriter
from django.contrib.gis.geos.prototypes.threadsafe import GEOSFunc
import psycopg2
from datetime import datetime
from subprocess import call, check_output
from sys import exit

start = datetime.now()
print "starting loadGeoNames at ", start

print "deleting all places",
for table in ["appfd_alias", "appfd_alternatename", "appfd_place"]:
    call("sudo -u postgres psql -c 'TRUNCATE " + table + " CASCADE;' dbfd", shell=True)
print "done"

output_file = open("/tmp/allCountriesCleaned.txt", "wb")
writer = csv.writer(output_file)

wkb_w = WKBWriter()
wkb_w.srid = True
print "writing output file"
with open("/tmp/allCountries.txt", "r") as f:
    counter = 0
    places_to_create = []
    for line in f:
      try:
        counter += 1
        geonameid, name, asciiname, alternatenames, latitude, longitude, feature_class, feature_code, country_code, cc2, admin1_code, admin2_code, admin3_code, admin4_code, population, elevation, dem, timezone, modification_date = line.split("\t")
        if feature_code == "ADM1": admin_level = "1"
        elif feature_code == "ADM2": admin_level = "2"
        elif feature_code == "ADM3": admin_level = "3"
        elif feature_code == "ADM4": admin_level = "4"
        elif feature_code == "ADM5": admin_level = "5"
        else: admin_level = ""
        point = wkb_w.write_hex(Point(float(longitude), float(latitude), srid=4326))
        writer.writerow([ counter, admin_level, admin1_code, admin2_code, "", country_code, "", "", geonameid, "", "", name, "", point, population, "", "", timezone ])
        if counter % 1000000 == 0:
             print counter, ":", str((datetime.now() - start).total_seconds()), "seconds so far"
      except Exception as e:
        print e

output_file.close()
print "closed output_file"

print "about to execute COPY"
call("""sudo -u postgres psql -c "COPY appfd_place FROM '/tmp/allCountriesCleaned.txt' WITH CSV;" dbfd""", shell=True)
print "executed statement"

total_seconds = (datetime.now() - start).total_seconds()
message = "Loading geonames took " + str(total_seconds) + " seconds."
print message
with open("log.txt", "wb") as f:
    f.write(message)
