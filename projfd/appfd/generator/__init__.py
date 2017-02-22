from appfd.extractor import extract_locations_from_text
from appfd.finisher import finish_order
from appfd.scripts.resolve import resolve_locations
from os import mkdir

def generate_map_from_sources(job, data_sources, metadata_sources):

    try:
        print "starting generate_map_from_sources"

        key = job['key']
        max_seconds = int(job.get('max_seconds', 10))
        countries = job.get('countries', [])
        admin1limits = job.get('admin1limits', [])


        # make directory to store input sources and final maps
        directory = "/home/usrfd/maps/" + key + "/"
        mkdir(directory)

        locations = []
        for source in data_sources:
            print "source:", source
            source_type = source['type']
            source_data = source['data']
            if source_type == "text":
                print "source_data:", source_data
                # http://stackoverflow.com/questions/1306631/python-add-list-to-set
                locations.extend(extract_locations_from_text(source_data))
  
        print "locations:", len(locations) 
        resolve_locations(locations, order_id=job['order_id'], max_seconds=max_seconds, countries=countries)

        print "finishing generate_map_from_sources"
        finish_order(job['key'])

    except Exception as e:
        print "EXCEPTION in generate_map_from_sources:", e
