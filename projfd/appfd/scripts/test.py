from datetime import datetime
from location_extractor import *
from os.path import isfile
import pickle
from resolve import *

def run():
  try:

    print "starting test"

    path_to_pickled_locations = "/tmp/locations.p"
    if isfile(path_to_pickled_locations):
        with open(path_to_pickled_locations) as f:
            locations = pickle.load(f)
    else:
        file_obj = open("/tmp/245365.pdf", "rb")
        locations = extract_locations_with_context(file_obj)
        file_obj.close()
        with open(path_to_pickled_locations, "wb") as f:
            pickle.dump(locations, f)

    start = datetime.now()
    features = resolve_locations(locations)
    print "features:", len(features)
    print "took", (datetime.now()-start).total_seconds()

  except Exception as e:
    print e
