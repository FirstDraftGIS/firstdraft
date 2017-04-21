from appfd.models import Test
from datetime import datetime
import csv, fdgis
from os import listdir, mkdir, remove
from os.path import dirname, realpath

fdgis.default_url_to_server = "http://localhost"

PATH_TO_DIRECTORY_OF_THIS_FILE = dirname(realpath(__file__))
PATH_TO_DIRECTORY_OF_INPUT_DATA = PATH_TO_DIRECTORY_OF_THIS_FILE + "/data/input"

def run(debug=True):

    try:

        if debug: print "starting test"


        number_of_correct_features = 0
        number_of_incorrect_features = 0


        filenames = listdir(PATH_TO_DIRECTORY_OF_INPUT_DATA)
        if debug: print "filenames:", filenames
        for filename in filenames:
            if debug: print "filename:", filename
            path_to_date = PATH_TO_DIRECTORY_OF_INPUT_DATA + "/" + filename
            for order in listdir(path_to_date):
                sources = []
                path_to_order = path_to_date + "/" + order
                if debug: print "path_to_order:", path_to_order

                path_to_source_data_folder = path_to_order + "/source_data"
                for filename in listdir(path_to_source_data_folder):
                    with open(path_to_source_data_folder + "/" + filename) as f:
                        sources.append(f.read())
                print "sources:", sources
                geojson = fdgis.make_map(sources)
                print "geojson:", geojson


                # test results
                correct = {}
                with open(path_to_order + "/results.tsv") as f:
                    for name, x, y in list(csv.reader(f, delimiter="\t"))[1:]:
                        try:
                            correct[name] = {"x": float(x), "y": float(y)}
                        except Exception as e:
                            print "x:", [x]
                            print "y:", [y]
                 
                if debug: print "correct:", correct 
                for feature in geojson['features']:
                    name = feature['properties']['name']
                    x, y = feature['geometry']['geometries'][0]['coordinates']
                    if debug: print "x:", x
                    if debug: print "y:", y
                    correct_props = correct.get(name, None)
                    if correct_props:
                        correct_x = correct_props['x']
                        correct_y = correct_props['y']
                        if debug: print "correct_props:", correct_props
                        if correct_x and correct_y and correct_x != "NONE" and correct_y != "NONE":
                            if correct_x == x and correct_y == y:
                                number_of_correct_features += 1
                            else:
                                number_of_incorrect_features += 1

        if debug: print "number_of_correct_features:", number_of_correct_features
        if debug: print "number_of_incorrect_features:", number_of_incorrect_features
        accuracy = float(number_of_correct_features) / (number_of_correct_features + number_of_incorrect_features)
        if debug: print "accuracy:", accuracy

        Test.objects.create(datetime=datetime.now(), accuracy=accuracy)

        if debug: print "finishing test"

    except Exception as e:

        print "CAUGHT EXCEPTION in ai.test:", e




