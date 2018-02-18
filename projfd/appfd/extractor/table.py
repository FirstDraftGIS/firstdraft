from appfd.models import Place
from bnlp3 import clean as bnlp_clean
from broth import Broth
from location_extractor import extract_locations_with_context, extract_locations_with_context_from_html_tables
from newspaper import Article
from scrp import getTextContentViaMarionette, getRandomUserAgentString
from requests import get

def extract_locations_from_tables(tables, debug=True):
  try:

    try:
        if debug: print("starting extract_locations_from_tables with", type(tables))#, tables
    except: pass

    locations = []

    location_column_names = ('city','community','country','neighborhood','loc','location','locations','place','province')

    for table in tables:
        top_lines = table[:10]
        header = table[0]
        number_of_columns = len(header)
        if debug: print("number_of_columns:", number_of_columns)

        location_column_index = None
        # erroneously assume that there is only one location column
        # looks quickly and see if keyword mentioned
        for index, column_name in enumerate(header):
            if (isinstance(column_name, str) or isinstance(column_name, str)) and column_name.lower().strip() in location_column_names:
                location_column_index = index

        if debug: print("couldn't get location_column_index quickly")

        if not location_column_index:
            for index in range(number_of_columns):
                print("index:", index)
                values = [row[index] for row in table if len(row) > index]
                types = set([type(value) for value in values])
                print("types:", types)

                irrelevant_types = (None, int, float)
                for _type in irrelevant_types:
                    try:
                        types.remove(_type)
                    except:
                        pass

                # assuming that place names can't be numbers
                if len(types) > 0:
                    # don't want to look up datetimes or numbers, only text
                    values = [value for value in values if isinstance(value, str) or isinstance(value, str)]
                    try:
                        if debug: print("values:", values)
                    except: pass
                    try:
                        count = Place.objects.filter(name__in=values).count()
                        print("count:", count)
                    except Exception as e:
                        print("FAILED TO GET COUNT:", e)
                        print("values:", values)
                    if count > 0:
                        location_column_index = index
                      
        print("doesn't handle repeats")
        print("location_column_index:", location_column_index)
        if location_column_index is not None:
            print("table:", table)
            for row in table:
                if row and len(row) > location_column_index:
                    name = row[location_column_index]
                    if name and not isinstance(name, int) and not isinstance(name, float):
                        d = {"count": 1, "name": name}
                        for column_index, column_name in enumerate(header):
                            d[column_name] = row[column_index]
                        locations.append(d)

    return locations

  except Exception as e:
    print("Caught Exception in extract_locations_from_tables:", e)
