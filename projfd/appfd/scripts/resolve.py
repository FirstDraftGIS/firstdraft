from appfd.models import *

# takes in a location as input text and returns the location
def resolve(text):
    print "starting resolve with text", text

    if text:
        #should give preference to citiesd
        # also locational culstering... expectation maximization algorithm??, number of clusters is dynamic...
        locations = Place.objects.filter(name=text).order_by('-population')
        count = locations.count()

        if count == 0:

            """
            print "count is 0"
            locations = Place.objects.filter(name__icontains=text).order_by('-population')
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
            """
            return None
                
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
    resolve(text=text)
