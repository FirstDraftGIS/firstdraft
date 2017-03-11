from appfd.models import Feature
from appfd.models import Order
from json import dumps
from os import mkdir
from os.path import isdir

def run(key):
    print "starting create_xypair with key " + key

    from django.db import connection
    connection.close()

    pairs = []
    for feature in Feature.objects.filter(order__token=key):

        fp = feature.featureplace_set.filter(correct=True).first()
        if fp:
            if fp.place:
                pairs.append([fp.place.point.x, fp.place.point.y])

    directory = "/home/usrfd/maps/" + key + "/"
    if not isdir(directory):
        mkdir(directory)

    if len(pairs) > 1:
        pair = pairs[0]
    elif len(pairs) == 1:
        pair = pairs[0]
    else:
        pair = []

    # run something here so it chooses the most precise one
    with open(directory + key + ".xy", "wb") as f:
        f.write(dumps(pair))
