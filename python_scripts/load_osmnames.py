from collections import Counter
import csv, shlex
from datetime import datetime
#from language_detector import detect_language
from os import devnull
from os.path import devnull, isfile
from os import remove
from re import match, search
from requests import get
from subprocess import call
from time import sleep
from urllib import urlretrieve
import sys



def run(debug=True, skip_cleaning=False):

    try:

        if debug: start = datetime.now()

        if debug: print "starting to import osmnames into First Draft"


        csv.field_size_limit(sys.maxsize)
        total_number_of_rows = 21055841

        path_to_gz = "/tmp/planet-latest.tsv.gz"
        path_to_tsv = "/tmp/planet-latest.tsv"
        if not isfile(path_to_tsv):

            if not isfile(path_to_gz):
                url = "https://github.com/OSMNames/OSMNames/releases/download/v1.1/planet-latest.tsv.gz"
                urlretrieve(url, path_to_gz)
                print "downloaded to " + path_to_gz

            call(["gunzip", path_to_gz, "--force"], cwd="/tmp")
            print "gunzipped"


        if debug: print "opening tsv"
        number_created = 0
        number_found = 0
        set_of_importance = set()


        path_to_cleaned_tsv = path_to_tsv.replace(".tsv", "-cleaned.tsv")

        #lengths = set()
        # preprocessing
        #counter = Counter()
      

        if not skip_cleaning:
            with open(path_to_cleaned_tsv, "wb") as cleaned_tsv:

                writer = csv.writer(cleaned_tsv, delimiter="\t", quotechar='"', quoting=csv.QUOTE_ALL)

                with open(path_to_tsv) as f:

                    reader = csv.reader(f, delimiter="\t", quotechar='"')

                    # skip first row
                    reader.next()

                    for row in reader:
                        #counter[len(row)] += 1
                        # checking that name is gonna fit in db
                        if len(row) == 23 and len(row[0]) < 200:
                            writer.writerow([column or "NULL" for column in row])

        #print "counter:", counter

        seconds = (datetime.now() - start).total_seconds()
        minutes = float(seconds) / 60
        print "took", minutes, "minutes to preprocess whole planet-latest.tsv file"

        if debug: start = datetime.now()
        statement = "SELECT load_osm_name(name, lat, lon, country_code, importance) FROM planet_latest"
        if debug: print "statement:", statement
        threshold = None
        if threshold:
            statement += " LIMIT " + str(threshold)
        bash_statement = "sudo -u postgres psql dbfd -c '" + statement + "';"
        print "bash_statement:", bash_statement
        args = shlex.split(bash_statement)
        print "args:", args
        FNULL = open(devnull, 'w')
        call(args, stdout=FNULL)

        if debug:
            seconds = (datetime.now() - start).total_seconds()
            seconds_per_line = float(seconds) / threshold
            minutes_per_line = float(seconds_per_line) / 60
            print "it would take ", minutes_per_line * total_number_of_rows / 60, "hours to complete"
            

    except Exception as e:

        print e

run()
