from apifd.serializers import PlaceSerializer
from appfd.models import Place
from appfd.resolver.additions import resolve_possible_additions

def generate_possible_additions(name, token):
    print "starting generate_possible_additions"

    # returns sorted by probability
    geoentities = resolve_possible_additions(name, token)

    print "resolved geoentities:", geoentities


    #for g in geoentities:
    #    print "g:", vars(g)
    place_ids = [g.place_id for g in geoentities]

    return sorted(list(Place.objects.filter(id__in=place_ids)), key=lambda place: place_ids.index(place.id))
