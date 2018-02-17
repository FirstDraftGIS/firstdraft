from appfd.geoentity import GeoEntity
from appfd.scripts.ai import predict
from datetime import datetime
from django.db import connection

def resolve_possible_additions(name, token):

    try:

        print("starting resolve_possible_additions with", name, token)

        start = datetime.now()

        statement = "SELECT * FROM get_candidates('" + name + "', '" + token +"');"

        print("statement:", statement)

        cursor = connection.cursor()
        cursor.execute(statement)

        geoentities = []
        for row in cursor.fetchall():
            try:
                geoentities.append(GeoEntity(row))
            except Exception as e:
                #print "row:", row
                print("exception creating geoentity... skipping")

        print("created " + str(len(geoentities)) + " geoentities")

        number_of_geoentities = len(geoentities)

        print("geoentities", type(geoentities), len(geoentities))

        if number_of_geoentities == 0:
            return False

        predict.run(geoentities)

        # sorting to put most likely first
        geoentities.sort(key=lambda geoentity: -1 * geoentity.probability)

        print("took:", (datetime.now() - start).total_seconds(), "seconds to resolve new additions")

        return geoentities

    except Exception as e:
        print(e)
