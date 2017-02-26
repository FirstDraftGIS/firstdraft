from appfd.models import Source
from appfd.extractor import extract_locations_from_text, extract_locations_from_webpage
from appfd.finisher import finish_order
from appfd.scripts.resolve import resolve_locations
from os import mkdir
from requests import head, get
import validators


def toFileName(text, max_length=1000):
    return url.replace("/","_").replace("\\","_").replace("'","_").replace('"',"_").replace(".","_").replace(":","_").replace("__","_").replace(" ","_")[:max_length]

def save_text_to_file(text, filepath):
    with open(filepath) as f:
        f.write(text.encode("utf-8"))

def generate_map_from_sources(job, data_sources, metadata_sources):

    try:
        print "starting generate_map_from_sources"

        key = job['key']
        max_seconds = int(job.get('max_seconds', 10))
        countries = job.get('countries', [])
        admin1limits = job.get('admin1limits', [])
        order_id = job['order_id']


        # make directory to store input sources and final maps
        directory = "/home/usrfd/maps/" + key + "/"
        mkdir(directory)

        locations = []
        for source in data_sources:
            try:
                print "source:", source
                source_type = source['type']
                source_data = source['data'].strip()
                if source_type == "text":
                    print "source_data:", source_data
                    Source.objects.create(order_id=order_id, source_text=source_data, source_type="text")
                    save_text_to_file(source_data, toFileName(source_data, max_length=20))
                    locations.extend(extract_locations_from_text(source_data))
                elif validators.url(source_data):
                    # make head request to get content type
                    if source_data.endswith(".doc"):
                        pass
                    elif source_data.endswith(".docx"):
                        pass
                    elif source_data.endswith(".pdf"):
                        pass
                    elif source_data.endswith(".zip"):
                        pass
                    else:
                        contentType = head(source_data, allow_redirects=True).headers['Content-Type']
                        if contentType.startswith("application/pdf"):
                            pass
                        elif contentType.startswith("text/html"):
                            print "seems to be a normal webpage"
                            Source.objects.create(order_id=order_id, source_url=source_data, source_type="url")
                            if "html" in source:
                                # if passing in html along with url
                                locations.extend(extract_locations_from_webpage(source_data, html=source['html']))
                            else:
                                locations.extend(extract_locations_from_webpage(source_data))
            except Exception as e:
                print "failed to get locations for source because", e
  
        print "locations:", len(locations) 
        resolve_locations(locations, order_id=job['order_id'], max_seconds=max_seconds, countries=countries)

        print "finishing generate_map_from_sources"
        finish_order(job['key'])

    except Exception as e:
        print "EXCEPTION in generate_map_from_sources:", e
