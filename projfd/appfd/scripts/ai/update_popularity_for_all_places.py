from appfd.models import Place
from datetime import datetime
from django.db import connection

# print calculate popularity for all places
def run():

    try:

        start = datetime.now()

        print "starting calc_popularity"

        cursor = connection.cursor()

        print "cursor:", cursor

        statement = "UPDATE appfd_place SET popularity = calc_popularity(id) WHERE id IN (SELECT place_id FROM appfd_featureplace INNER JOIN appfd_feature ON (appfd_featureplace.feature_id = appfd_feature.id) WHERE appfd_feature.verified = true);"

        print "statement:", statement

        cursor.execute(statement)

        print "calculating popularity took " + str((datetime.now() - start).total_seconds()) + " seconds"

    except Exception as e:

        print e
