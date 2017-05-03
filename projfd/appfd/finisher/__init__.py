from appfd.models import Order
from appfd.scripts.create import create_csv, create_geojson, create_images, create_shapefiles, create_xypair, create_pdf
from appfd.scripts.ai import update_country_code_ranks_for_order
from apifd.scripts.create.frequency_geojson import run as create_frequency_geojson
from multiprocessing import Process


# don't update popularity here because that method only works on features that have been verified
def finish_order(key):

    try:

        print "starting finish order with", key

        map_format = Order.objects.get(token=key).map_format

        if map_format == "all":
            for _method in (create_geojson.run, create_frequency_geojson, create_shapefiles.run, create_csv.run, create_images.run, create_xypair.run, create_pdf.run):
                Process(target=_method, args=(key,)).start()
        elif map_format == "geojson":
            Process(target=create_geojson.run, args=(key,)).start()
        elif map_format == "csv":
            Process(target=create_csv.run, args=(key,)).start()
        elif map_format in ['gif', 'jpg', 'png']:
            Process(target=create_images.run, args=(key,)).start()
        elif map_format == 'pdf':
            Process(target=create_pdf.run, args=(key,)).start()
        elif map_format == 'shp':
            Process(target=create_shapefiles.run, args=(key,)).start()
        elif map_format == "xy":
            Process(target=create_xypair.run, args=(key,)).start()


        # update country code ranks sometime
        Process(target=update_country_code_ranks_for_order.run, args=(key,)).start()

        from django.db import connection
        connection.close()
        order = Order.objects.get(token=key).finish()
        print "finished order", order

    except Exception as e:

        print "EXCEPTION in finish_order:", e
