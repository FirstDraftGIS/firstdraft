from appfd.models import Source
from appfd.extractor import extract_locations_from_tables, extract_locations_from_text, extract_locations_from_webpage
from appfd.finisher import finish_order
from appfd.styler import style_order
from appfd.resolver import resolve_locations
from location_extractor import extract_locations_with_context_from_docx, extract_locations_with_context_from_pdf
from io import BytesIO
from os import mkdir
from os.path import join
from projfd.additional_settings.firstdraft import MAPS_DIRECTORY
from requests import head, get
from table_extractor import extract_tables
import validators

def toFileName(text, max_length=1000):
    return text.replace("/","_").replace("\\","_").replace("'","_").replace('"',"_").replace(".","_").replace(":","_").replace("__","_").replace(" ","_")[:max_length]

def save_text_to_file(text, filepath):
    with open(filepath, "wb") as f:
        f.write(text.encode("utf-8"))

def generate_map_from_sources(job, data_sources, metadata_sources, debug=False):

    try:
        print("starting generate_map_from_sources w job")

        key = job['key']
        max_seconds = int(job.get('max_seconds', 10))
        countries = job.get('countries', [])
        admin1limits = job.get('admin1limits', [])
        order_id = job['order_id']
        extra_context = job.get("extra_context", {})
        end_user_timezone = extra_context.get("end_user_timezone", None)
        case_insensitive = extra_context.get("case_insensitive", None)

        # make directory to store input sources and final maps
        directory = join(MAPS_DIRECTORY, key)
        mkdir(directory)
        print("made directory:" + directory)

        max_source_text_length = next(f for f in Source._meta.fields if f.name == "source_text").max_length

        locations = []
        for source in data_sources:
            try:
                print("source:", source)
                source_type = source['type']
                source_data = source['data']
                if source_type == "text":
                    print("source_data:", source_data.encode("utf-8"))
                    print("[generator] creating source object")
                    source_text = source_data.encode("utf-8") if len(source_data.encode("utf-8")) < max_source_text_length else None
                    Source.objects.create(order_id=order_id, source_text=source_text, source_type="text")
                    print("[generator] created source object")
                    #save_text_to_file(source_data, toFileName(source_data, max_length=20))
                    locations.extend(extract_locations_from_text(source_data, case_insensitive=case_insensitive))
                elif (isinstance(source_data, str) or isinstance(source_data, str)) and validators.url(source_data):
                    print("source is url")

                    url = source_data.strip().strip('"').strip('"')

                    # we want to respect Google, so we avoid adding an automated click through
                    # by just directly getting the url
                    if url.startswith("https://www.google.com/url?"):
                        url = unquote(search("(?<=&url=)[^&]{10,}", url).group(0))

                    if not url.startswith("http"):
                        print("we assume that the user didn't include the protocol")
                        url = "http://" + url

                    Source.objects.create(order_id=order_id, source_url=url, source_type="url")

                    extension = url.split(".")[-1]
                    print("extension:", extension)
                    
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
                        locations.extend(extract_locations_from_text(get(url).content, case_insensitive=case_insensitive))
                    elif url.endswith(".zip"):
                        pass
                    else:
                        contentType = head(url, allow_redirects=True).headers['Content-Type']
                        if contentType.startswith("application/pdf"):
                            locations.extend(extract_locations_with_context_from_pdf(BytesIO(get(url).content)))
                        elif contentType.startswith("text/html"):
                            print("seems to be a normal webpage")
                            if "html" in source:
                                print("passing along html with url")
                                locations.extend(extract_locations_from_webpage(url, html=source['html']))
                            else:
                                locations.extend(extract_locations_from_webpage(url, debug_level=0))
                elif source_type == "file":
                    print("source_type is file")
                    print("source_data:", source_data, dir(source_data))
                    print("source_data.name:", source_data.name)
                    source_data_name = source_data.name
                    source_extension = source_data_name.split(".")[-1]
                    if source_extension == "docx":
                        locations.extend(extract_locations_with_context_from_docx(source_data))
                        locations.extend(extract_locations_from_tables(extract_tables(source_data)))
                    elif source_extension in ("csv", "tsv", "xls", "xlsm", "xlsx"):
                        locations.extend(extract_locations_from_tables(extract_tables(source_data)))
                    elif source_extension == "txt":
                        locations.extend(extract_locations_from_text(source_data.read(), case_insensitive=case_insensitive))
                    elif source_extension == "pdf":
                        print("source_extension is pdf")
                        locations.extend(extract_locations_with_context_from_pdf(source_data))
                    
 
            except Exception as e:
                print("failed to get locations for source because", e)
  
        print("[generate_map_from_sources] locations before resolving:", len(locations)) 
        resolve_locations(locations, order_id=order_id, max_seconds=max_seconds, countries=countries, end_user_timezone=end_user_timezone, case_insensitive=case_insensitive, debug=debug)

        print("job.keys():", list(job.keys()))
        if "style" in job:
            style_order(order_id=order_id, style=job['style'])
        else:
            style_order(order_id=order_id)

        print("finishing generate_map_from_sources")
        finish_order(job['key'])

    except Exception as e:
        print("EXCEPTION in generate_map_from_sources:", e)
