import csv, subprocess
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import Point
from django.contrib.gis.geos import fromstr
from django.contrib.gis.geos import Point, WKBWriter
from django.contrib.gis.geos.prototypes.threadsafe import GEOSFunc
import psycopg2
from datetime import datetime
from subprocess import call, check_output
from sys import argv, exit

start = datetime.now()
print "starting loadGeoNames at ", start

dry_run = len(argv) == 2 and argv[1] == "dry-run"
print "dry_run:", dry_run

print "deleting all places",
for table in ["appfd_alias", "appfd_alternatename", "appfd_place"]:
    call("sudo -u postgres psql -c 'TRUNCATE " + table + " CASCADE;' dbfd", shell=True)
print "done"

delimiter = "\t"
null = "null"

output_file = open("/tmp/allCountriesCleaned.txt", "wb")
writer = csv.writer(output_file, delimiter=delimiter)

first_columns = [[column.strip() for column in line.split("|")][0] for line in check_output("sudo -u postgres psql dbfd -c '\d+ appfd_place'", shell=True).splitlines()]
order_of_columns = first_columns[first_columns.index("id"):first_columns.index("Indexes:")]
print "order_of_columns:", order_of_columns

wkb_w = WKBWriter()
wkb_w.srid = True
print "writing output file"
with open("/tmp/allCountries.txt", "r") as f:
    counter = 0
    places_to_create = []
    for line in f:
      try:
        counter += 1
        values = dict(zip(["geonameid", "name", "asciiname", "alternatenames", "latitude", "longitude", "feature_class", "feature_code", "country_code", "cc2", "admin1_code", "admin2_code", "admin3_code", "admin4_code", "population", "elevation", "dem", "timezone", "modification_date"], line.split("\t")))
        values["id"] = counter
        feature_code = values['feature_code']
        if feature_code == "ADM1": admin_level = "1"
        elif feature_code == "ADM2": admin_level = "2"
        elif feature_code == "ADM3": admin_level = "3"
        elif feature_code == "ADM4": admin_level = "4"
        elif feature_code == "ADM5": admin_level = "5"
        else: admin_level = "null"
        values["admin_level"] = admin_level
        values['point'] = wkb_w.write_hex(Point(float(values['longitude']), float(values['latitude']), srid=4326))
        writer.writerow([values.get(column_name, null) for column_name in order_of_columns])
        if counter % 100000 == 0:
             print counter, ":", str((datetime.now() - start).total_seconds()), "seconds so far"
             if dry_run:
                 print "it's a dry_run so don't load all places"
                 break
      except Exception as e:
        print e

output_file.close()
print "closed output_file"

print "about to execute COPY"
# defaults to using text format with tab separator
call("""sudo -u postgres psql -c "COPY appfd_place FROM '/tmp/allCountriesCleaned.txt' WITH DELIMITER '""" + delimiter + """' NULL '""" + null + """';" dbfd""", shell=True)
print "executed statement"

total_minutes = (datetime.now() - start).total_seconds() / 60
message = "Loading geonames took " + str(total_minutes) + " minutes."
print message
with open("log.txt", "wb") as f:
    f.write(message)
