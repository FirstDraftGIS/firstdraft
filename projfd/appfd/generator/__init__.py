from appfd.models import Source
from appfd.extractor import extract_locations_from_tables, extract_locations_from_text, extract_locations_from_webpage
from appfd.finisher import finish_order
from appfd.scripts.resolve import resolve_locations
from location_extractor import extract_locations_with_context_from_docx, extract_locations_with_context_from_pdf
from io import BytesIO
from os import mkdir
from requests import head, get
from table_extractor import extract_tables
import validators


def toFileName(text, max_length=1000):
    return text.replace("/","_").replace("\\","_").replace("'","_").replace('"',"_").replace(".","_").replace(":","_").replace("__","_").replace(" ","_")[:max_length]

def save_text_to_file(text, filepath):
    with open(filepath, "wb") as f:
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
                source_data = source['data']
                if source_type == "text":
                    print "source_data:", source_data
                    Source.objects.create(order_id=order_id, source_text=source_data, source_type="text")
                    #save_text_to_file(source_data, toFileName(source_data, max_length=20))
                    locations.extend(extract_locations_from_text(source_data))
                elif (isinstance(source_data, unicode) or isinstance(source_data, str)) and validators.url(source_data):
                    print "source is url"

                    url = source_data.strip().strip('"').strip('"')

                    # we want to respect Google, so we avoid adding an automated click through
                    # by just directly getting the url
                    if url.startswith("https://www.google.com/url?"):
                        url = unquote(search("(?<=&url=)[^&]{10,}", url).group(0))

                    if not url.startswith("http"):
                        print "we assume that the user didn't include the protocol"
                        url = "http://" + url

                    Source.objects.create(order_id=order_id, source_url=url, source_type="url")

                    extension = url.split(".")[-1]
                    print "extension:", extension
                    
                    # make head request to get content type
                    if extension in ("csv", "tsv", "xls", "xlsm", "xlsx"):
                        locations.extend(extract_locations_from_tables(extract_tables(url)))
                    elif url.endswith(".doc"):
                        pass
                    elif url.endswith(".docx"):
                        locations.extend(extract_locations_with_context_from_docx(BytesIO(get(url).content)))
                        locations.extend(extract_locations_from_tables(extract_tables(source_data)))
                    elif url.endswith(".pdf"):
                        locations.extend(extract_locations_with_context_from_pdf(BytesIO(get(url).content)))
                    elif url.endswith(".txt"):
                        locations.extend(extract_locations_from_text(get(url).content))
                    elif url.endswith(".zip"):
                        pass
                    else:
                        contentType = head(url, allow_redirects=True).headers['Content-Type']
                        if contentType.startswith("application/pdf"):
                            locations.extend(extract_locations_with_context_from_pdf(BytesIO(get(url).content)))
                        elif contentType.startswith("text/html"):
                            print "seems to be a normal webpage"
                            if "html" in source:
                                # if passing in html along with url
                                locations.extend(extract_locations_from_webpage(url, html=source['html']))
                            else:
                                locations.extend(extract_locations_from_webpage(url))
                elif source_type == "file":
                    print "source_type is file"
                    print "source_data:", source_data, dir(source_data)
                    print "source_data.name:", source_data.name
                    source_data_name = source_data.name
                    source_extension = source_data_name.split(".")[-1]
                    if source_extension == "docx":
                        locations.extend(extract_locations_with_context_from_docx(source_data))
                        locations.extend(extract_locations_from_tables(extract_tables(source_data)))
                    elif source_extension in ("csv", "tsv", "xls", "xlsm", "xlsx"):
                        locations.extend(extract_locations_from_tables(extract_tables(source_data)))
                    elif source_extension == "txt":
                        locations.extend(extract_locations_from_text(source_data.read()))
                    
 
            except Exception as e:
                print "failed to get locations for source because", e
  
        print "locations:", len(locations) 
        resolve_locations(locations, order_id=job['order_id'], max_seconds=max_seconds, countries=countries)

        print "finishing generate_map_from_sources"
        finish_order(job['key'])

    except Exception as e:
        print "EXCEPTION in generate_map_from_sources:", e
