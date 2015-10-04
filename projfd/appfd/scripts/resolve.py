from appfd.models import *
from django.db.models import Q

# takes in a location as input text and returns the location
def resolve(text):
    print "starting resolve with text", text

    if text:
        #should give preference to citiesd
        # also locational culstering... expectation maximization algorithm??, number of clusters is dynamic...
        # order by admin level, so have higher chance of getting the country of Spain than some city called Spain
        locations = Place.objects.filter(name=text).order_by('admin_level','-population')
        count = locations.count()

        if count == 0:
            print "count is 0"
            locations = Place.objects.filter(aliases__alias=text).order_by('admin_level','-population')
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
            return locations[0]
            # should also do locational clustering and if any points are more than two standard deviations away, look for other example

def run(text=None):
    print "running resolve with ", text
    print "resolved", resolve(text=text)
