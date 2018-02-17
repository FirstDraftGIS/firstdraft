from appfd.models import Place
from bnlp import trim_location

def run():
    for index, place in enumerate(Place.objects.filter(admin_level=0)):
        name = place.name
        print(index,":",name)
        trimmed = trim_location(place.name)
        print("    trimmed:", trimmed)
        place.name = trimmed
        place.save()
