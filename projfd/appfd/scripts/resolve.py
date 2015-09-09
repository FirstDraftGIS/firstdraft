from appfd.models import *

# takes in a location as input text and returns the location
def resolve(text):

    locations = Place.objects.filter(name=text)
    count = locations.count()

    if count == 0:
        print "count is 0"
    elif count == 1:
        return locations[0]
    else: # count > 1
        print "count is greater than 1"
        print "    locations are", locations

