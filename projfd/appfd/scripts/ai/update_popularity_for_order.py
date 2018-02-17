from appfd.models import Order, Place
from datetime import datetime
from django.db import connection

# print calculate popularity for places mentioned in order
def run(token):

    try:

        start = datetime.now()

        print("starting update_popularity_for_order with token", token)

        # resets connection because multiprocessing
        connection.close()

        cursor = connection.cursor()

        print("cursor:", cursor)

        statement = "UPDATE appfd_place SET popularity = calc_popularity(id) WHERE id IN (SELECT place_id FROM appfd_featureplace INNER JOIN appfd_feature ON (appfd_featureplace.feature_id = appfd_feature.id) WHERE appfd_feature.order_id = (SELECT id FROM appfd_order WHERE token = '" + token + "') AND appfd_feature.verified = true);"

        print("statement:", statement)

        cursor.execute(statement)

        print("calculating popularity took " + str((datetime.now() - start).total_seconds()) + " seconds")

    except Exception as e:

        print(e)
