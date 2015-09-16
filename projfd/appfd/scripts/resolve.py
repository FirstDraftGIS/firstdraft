from appfd.models import *

# takes in a location as input text and returns the location
def resolve(text):

    if text:
        locations = Place.objects.filter(name=text)
        count = locations.count()

        if count == 0:
            print "count is 0"
            locations = Place.objects.filter(name__icontains=text)
            print "locations icontains are", locations
            count = locations.count()
            if count == 0:
                print "count is still 0"
            elif count == 1:
                print "count is 1"
                return locations[0]
            else:
                print "count > 0"
                return locations[0]
                
        elif count == 1:
            print "count is 1 so returning", locations[0]
            return locations[0]
        else: # count > 1
            print "count is greater than 1"
            print "    locations are", locations

def run(text=None):
    resolve(text=None)
