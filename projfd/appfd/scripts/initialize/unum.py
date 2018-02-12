from csv import DictReader, DictWriter
from django.contrib.gis.geos import Point
from django.db import connection
from pprint import PrettyPrinter

from appfd.models import Place

input_path = "/tmp/unum.tsv"
output_path = "/tmp/new_places_from_unum.tsv"

mapping = [
    ("admin1code", "admin1_code"),
    ("admin2code", "admin2_code"),
    ("admin3code", "admin3_code"),
    ("admin4code", "admin4_code"),
    ("asciiname", "name_ascii"),
    ("alternate_names", "other_names"),
    ("display_name", "name_display"),
    ("geoname_feature_class", "geonames_feature_class"),
    ("geoname_feature_code", "geonames_feature_code"),
    ("geonameid", "geonames_id")
]

def write_header(fieldnames):
    with open(output_path, "w") as output_file:
        DictWriter(output_file, delimiter="\t", fieldnames=fieldnames).writeheader()
    #with open(output_path, "w") as f:
    #    f.write("")

def write_line(fieldnames, line):
    with open(output_path, "a") as output_file:
        DictWriter(output_file, delimiter="\t", fieldnames=fieldnames).writerow(line)

def run():

    try:

        pp = PrettyPrinter(indent=4)

        connection.cursor().execute("TRUNCATE TABLE appfd_place CASCADE")

        output_fieldnames = [field.name for field in Place._meta.fields]

        with open(input_path) as input_file:
            reader = DictReader(input_file, delimiter="\t")

            write_header(output_fieldnames)
   
            count = 0
            for line in reader:
                count += 1
                if count > 1000:
                    exit()
                #line["id"] = count
                line["point"] = Point(float(line["latitude"]), float(line["longitude"]), srid=4326).ewkt
                for inkey, outkey in mapping:
                    line[outkey] = line.pop(inkey)
                    
                write_line(output_fieldnames, line) 

                #pp.pprint(line)

                if count % 10000:
                    Place.objects.from_csv(output_path, delimiter="\t")
                    write_header(output_fieldnames)

        print("finishing processing unum")

    except Exception as e:
        print(e)
