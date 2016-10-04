from appfd.models import Feature
from appfd.models import Order
import shapefile
from os import listdir, mkdir, remove
from os.path import basename, isdir
from zipfile import ZipFile

def run(key):
    print "starting create_shapefiles with key " + key

    from django.db import connection
    connection.close()

    directory = "/home/usrfd/maps/" + key + "/"
    if not isdir(directory):
        mkdir(directory)


    writer_points = shapefile.Writer(shapefile.POINT)
    writer_polygons = shapefile.Writer(shapefile.POLYGONM)

    # makes sure dbf and shapes are in sync
    writer_points.autoBalance = 1
    writer_polygons.autoBalance = 1

    # set shape type to point
    #writer_points.shapeType = 1
    #writer_polygons.shapeType = 25

    # turns to true if want to write mpoly
    wrote_mpoly = False

    # create fields
    for writer in [writer_points, writer_polygons]:
        writer.field("name")
        writer.field("confidence")
        writer.field("countrycode")
        writer.field("geonameid")
        writer.field("pcode")
        writer.field("start_time")
        writer.field("end_time")

    features = []
    for feature in Feature.objects.filter(order__token=key):

        fp = feature.featureplace_set.filter(correct=True).first()
        if fp:

            end = feature.end.strftime('%y-%m-%d') if feature.end else None
            start = feature.start.strftime('%y-%m-%d') if feature.start else None

            place = fp.place

            # what happens to feature.confidence decimal??? need to convert to float?
            writer_points.record(place.name.encode("utf-8"), fp.confidence, place.country_code, place.geonameid, place.pcode, start, end)
            writer_points.point(float(place.point.x), float(place.point.y))

            if place.mpoly:
                wrote_mpoly = True 
                writer_polygons.record(place.name.encode("utf-8"), fp.confidence, place.country_code, place.geonameid, place.pcode, start, end)
                coords = place.mpoly.coords
                if len(coords) == 1:
                    coords = coords[0]
                    writer_polygons.poly(parts=coords, shapeType=shapefile.POLYGONM)
                else:
                    print "Uh Uh we found an mpoly with more than one polygon, just take first one"
                    print "pyshp doesn't seem to be able to handle mpoly with original coords"
                    coords = coords[0]
                    writer_polygons.poly(parts=coords, shapeType=shapefile.POLYGONM)

    directory = "/home/usrfd/maps/" + key + "/"
    writer_points.save(directory + key + "_points")
    if wrote_mpoly:
        writer_polygons.save(directory + key + "_polygons")

    with ZipFile(directory + key + ".zip", 'w') as zipped_shapefile:
        for filename in listdir(directory):
            if filename.split(".")[-1] in ("cpg","dbf","shp","shx","prj"):
                path_to_file = directory + filename
                zipped_shapefile.write(path_to_file, filename)
                remove(path_to_file)

    print "finished creating shapefiles"
