from appfd.models import Feature
from appfd.models import Order
from django.contrib.gis.geos import MultiPolygon, Polygon
import shapefile
from shapefile import POLYGONM, POINT
from os import listdir, mkdir, remove
from os.path import basename, isdir
from zipfile import ZipFile

CRS = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]'

def area(coords):
    length = len(coords)
    if length >= 1:
        ext_coords = coords[0]
    if length >= 2:
        int_coords = coords[1]
    return Polygon(ext_coords, int_coords).area

def run(key, debug=False):

  try:
    print("starting create_shapefiles with key " + key)

    from django.db import connection
    connection.close()

    directory = "/home/usrfd/maps/" + key + "/"
    if not isdir(directory):
        mkdir(directory)


    writer_points = shapefile.Writer(POINT)
    writer_polygons = shapefile.Writer(POLYGONM)

    # makes sure dbf and shapes are in sync
    writer_points.autoBalance = 1
    writer_polygons.autoBalance = 1

    # set shape type to point
    #writer_points.shapeType = 1
    #writer_polygons.shapeType = 25

    # create fields
    for writer in [writer_points, writer_polygons]:
        writer.field("name")
        writer.field("confidence")
        writer.field("countrycode")
        writer.field("geonameid")
        writer.field("pcode")
        writer.field("start_time")
        writer.field("end_time")

    number_of_points = 0
    number_of_polygons = 0
    for feature in Feature.objects.filter(order__token=key):

        fp = feature.featureplace_set.filter(correct=True).first()
        if fp:

            end = feature.end.strftime('%y-%m-%d') if feature.end else None
            start = feature.start.strftime('%y-%m-%d') if feature.start else None

            place = fp.place

            # what happens to feature.confidence decimal??? need to convert to float?
            writer_points.record(place.name.encode("utf-8"), fp.confidence, place.country_code, place.geonameid, place.pcode, start, end)
            writer_points.point(float(place.point.x), float(place.point.y))
            number_of_points += 1

            try:
                if place.mpoly:
                    #print "pyshp doesn't seem to be able to handle mpoly with original coords"
                    for c in place.mpoly.coords:
                        writer_polygons.record(place.name.encode("utf-8"), fp.confidence, place.country_code, place.geonameid, place.pcode, start, end)
                        writer_polygons.poly(parts=c, shapeType=POLYGONM)
                        number_of_polygons += 1
            except Exception as e:
                print("caught the following error while trying to write multipolygons", e)

    directory = "/home/usrfd/maps/" + key + "/"
    if number_of_points > 0 or number_of_polygons > 0:
        if number_of_points > 0:
            writer_points.save(directory + key + "_points")
            with open(directory + key + "_points.prj", "wb") as f:
                f.write(CRS)
            print("WROTE PRJ")
        if number_of_polygons > 0:
            writer_polygons.save(directory + key + "_polygons")
            with open(directory + key + "_polygons.prj", "wb") as f:
                f.write(CRS)

        with ZipFile(directory + key + ".zip", 'w') as zipped_shapefile:
            for filename in listdir(directory):
                if filename.split(".")[-1] in ("cpg","dbf","shp","shx","prj"):
                    path_to_file = directory + filename
                    zipped_shapefile.write(path_to_file, filename)
                    remove(path_to_file)

    print("finished creating shapefiles")

  except Exception as e:
    print("CAUGHT EXCEPTION in create_shapefiles:", e)
