from appfd.models import Feature
from appfd.models import Order
from os import mkdir
from os.path import isdir

def run(key):
    print "starting create_csv with key " + key

    directory = "/home/usrfd/maps/" + key + "/"
    if not isdir(directory):
        mkdir(directory)

    path_to_csv_file = directory + key + ".csv"

    f = open(path_to_csv_file, "wb")

    features = Feature.objects.filter(order__token=key)

    field_names = ["name","confidence","latitude","longitude","country_code","geonameid"]

    write_pcode = any(feature.place.pcode for feature in features)
    if write_pcode:
        field_names.append("pcode")
    
    write_times = any(feature.end or feature.start for feature in features)
    if write_times:
        field_names.append("start_time")
        field_names.append("end_time")

    write_mpoly = any(feature.place.mpoly for feature in features)
    if write_mpoly:
        field_names.append("mpoly")

    f.write(",".join(field_names))

    for feature in features:

        place = feature.place

        f.write("\n" + place.name.encode("utf-8") + "," + feature.confidence + "," + str(place.point.x) + "," + str(place.point.y) + "," + str(place.country_code) + "," + str(place.geonameid))

        if write_pcode:
            if place.pcode:
                f.write(","+str(place.pcode))
            else:
                f.write(",")

        if write_times:
            if feature.start:
                f.write(","+feature.start.strftime('%y-%m-%d'))
            else:
                f.write(",")
            if feature.end:
                f.write(","+feature.end.strftime('%y-%m-%d'))
            else:
                f.write(",")
 
        if write_mpoly:
            if place.mpoly:
                f.write(","+str(place.mpoly.coords))
            else:
                f.write(",")

    f.close()

    print "finished creating csv"