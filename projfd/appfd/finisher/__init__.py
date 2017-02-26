from appfd.models import Order
from appfd.scripts import create_csv, create_geojson, create_images, create_shapefiles
from apifd.scripts.create.frequency_geojson import run as create_frequency_geojson
from multiprocessing import Process


def finish_order(key):

    try:

        print "starting finish order with", key

        for _method in create_geojson.run, create_frequency_geojson, create_shapefiles.run, create_csv.run, create_images.run:
            Process(target=_method, args=(key,)).start()

        from django.db import connection
        connection.close()
        order = Order.objects.get(token=key).finish()
        print "finished order", order

    except Exception as e:
        print "EXCEPTION in finish_order:", e
