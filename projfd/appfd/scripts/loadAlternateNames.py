from appfd.models import *
from django.db import connection, transaction
from datetime import datetime
from os.path import isfile
from urllib import urlretrieve
from zipfile import ZipFile

def run():
    start = datetime.now()
    print "starting loadAlternateNames at ", start
    
    path_to_dir = '/home/usrfd/data/geonames/'
    path_to_zip = path_to_dir + 'alternateNames.zip'
    if not isfile(path_to_zip):
        print "retrieving alternateNames.zip . . . ",
        urlretrieve('http://download.geonames.org/export/dump/alternateNames.zip', path_to_zip)
        print "done"
        print "unzipping alternateNames.zip . . . ",
        with ZipFile(path_to_zip, "r") as z:
            z.extractall(path_to_dir)
        print "done"

    # truncate existing AlternateName table
    cursor = connection.cursor()
    cursor.execute("TRUNCATE appfd_alias CASCADE")
    cursor.execute("TRUNCATE appfd_aliasplace CASCADE")

    throughs_to_create = []
    with open(path_to_dir + 'alternateNames.txt') as f:
        counter = 0
        for line in f:
            counter += 1
            geonameid, _, language, alternate_name, _, _, _, _ = line.decode("utf-8").split("\t")
            alias_id = ((Alias.objects.filter(alias=alternate_name) or [None])[0] or Alias.objects.create(alias=alternate_name, language=language)).id
            place_id = (Place.objects.filter(geonameid=geonameid).values_list("id", flat=True) or [None])[0]
            if place_id:
                AliasPlace.objects.get_or_create(alias_id=alias_id, place_id=place_id)
            if counter % 1000 == 0:
                print "line: " + str(counter)

    end = datetime.now()
    total_seconds = (end - start).total_seconds()
    print "total_seconds = ", total_seconds
    with open("log.txt", "a") as f:
        f.write("Loading alternateNames took " + str(total_seconds) + " seconds.")
