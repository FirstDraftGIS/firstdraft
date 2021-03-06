from json import dumps
from os import mkdir
from os.path import isdir, join

from appfd.models import Feature
from appfd.models import Order
from projfd.additional_settings.firstdraft import MAPS_DIRECTORY

def run(key):
    print("starting create_xypair with key " + key)

    from django.db import connection
    connection.close()

    pairs = []
    for feature in Feature.objects.filter(order__token=key):

        fp = feature.featureplace_set.filter(correct=True).first()
        if fp:
            if fp.place:
                pairs.append([fp.place.point.x, fp.place.point.y])

    directory = join(MAPS_DIRECTORY, key)
    if not isdir(directory):
        mkdir(directory)

    if len(pairs) > 1:
        pair = pairs[0]
    elif len(pairs) == 1:
        pair = pairs[0]
    else:
        pair = None

    # run something here so it chooses the most precise one
    with open(join(directory, key + ".xy"), "w") as f:
        f.write(dumps(pair))
