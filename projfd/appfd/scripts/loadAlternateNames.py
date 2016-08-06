from appfd.models import *
from django.db import connection, transaction
from django.db.utils import IntegrityError
from datetime import datetime
from os.path import isfile
from urllib import urlretrieve
from zipfile import ZipFile
from sys import exit

def run():
    start = datetime.now()
    print "starting loadAlternateNames at ", start
    
    path_to_dir = "/tmp/"
    path_to_zip = path_to_dir + 'alternateNames.zip'
    if not isfile(path_to_zip):
        print "retrieving alternateNames.zip . . . ",
        urlretrieve('http://download.geonames.org/export/dump/alternateNames.zip', path_to_zip)
        print "done"
        print "unzipping alternateNames.zip . . . ",
        with ZipFile(path_to_zip, "r") as z:
            z.extractall(path_to_dir)
        print "done"

    # connect to db
    cursor = connection.cursor()

    # create stored procedure for loading geonames row
    cursor.execute("""

    CREATE OR REPLACE FUNCTION 

    loadGeonamesRow(name text, lang text, gid integer)
    
    RETURNS void AS '

    DECLARE
        aliasid int;
        placeid int;

    BEGIN

    aliasid := (SELECT id FROM appfd_alias WHERE alias = $$name$$ LIMIT 1);
    IF aliasid IS NULL THEN
        INSERT INTO appfd_alias (alias, language) VALUES ($$name$$, lang) RETURNING id INTO aliasid;
    END IF;

    placeid := (SELECT id FROM appfd_place WHERE geonameid = gid);

    IF placeid IS NOT NULL THEN

        INSERT INTO appfd_aliasplace (alias_id, place_id) VALUES (aliasid, placeid);

    END IF;

    END; '

    LANGUAGE PLPGSQL;

    """)


    with open(path_to_dir + 'alternateNames.txt') as f:
        counter = 0
        for line in f:
            counter += 1
            geonameid, _, language, alternate_name, _, _, _, _ = line.decode("utf-8").split("\t")

            try:
                cursor.execute(u"SELECT loadGeonamesRow('" + alternate_name + "','" + language + "'," + geonameid + ")")
            except IntegrityError as e:
                pass

            if counter % 10000 == 0:
                print "line " + str(counter) + ": " + str((datetime.now() - start).total_seconds()) + " seconds"

    end = datetime.now()
    total_seconds = (end - start).total_seconds()
    print "total_seconds = ", total_seconds
    with open("log.txt", "wb") as f:
        f.write("Loading alternateNames took " + str(total_seconds) + " seconds.")
