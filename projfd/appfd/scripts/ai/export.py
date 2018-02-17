from appfd.models import Feature, Order, Place, Source
from appfd.scripts.ai.predict import get_df_from_features
import csv
from datetime import datetime
from os import mkdir
from os.path import dirname, realpath
from pandas import DataFrame

path_to_directory_of_this_file = dirname(realpath(__file__))

# used to create csv that other fdgis instances can read in to train their models
def run():
    try:
        print("starting export")

        path_to_folder = path_to_directory_of_this_file + "/data/output/" + datetime.now().isoformat().split(".")[0].replace(":","-").replace("T","-")
        mkdir(path_to_folder)
        
        for order_number, order in enumerate(Order.objects.filter(feature__verified=True)):
            path_to_order_folder = path_to_folder + "/" + str(order_number)
            mkdir(path_to_order_folder)

            path_to_sources_tsv = path_to_order_folder + "/sources.tsv"
            sources_tsv = open(path_to_sources_tsv, "wb")
            writer = csv.writer(sources_tsv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["#", "type"])

            path_to_source_data_folder = path_to_order_folder + "/source_data"
            mkdir(path_to_source_data_folder)
            for source_number, source in enumerate(Source.objects.filter(order=order)):
                writer.writerow([source_number, source.source_type])
                with open(path_to_source_data_folder + "/" + str(source_number) + ".txt", "wb") as f:
                    if source.source_type == "text":
                        f.write(source.source_text.encode("utf-8"))
                    elif source.source_type == "url":
                        f.write(source.source_url.encode("utf-8"))
            sources_tsv.close()

            #output results for each name
            results = open(path_to_order_folder + "/results.tsv", "wb")
            writer = csv.writer(results, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["name", "x", "y"])
            features = Feature.objects.filter(order=order)
            for name in features.values_list("name", flat=True).distinct():
                feature = features.get(name=name)
                if feature.verified:
                    place = Place.objects.filter(featureplace__feature__in=features, featureplace__feature__name=name, featureplace__correct=True).first()
                    if place:
                        writer.writerow([name, place.point.x, place.point.y])
                    else:
                        writer.writerow([name, "NONE", "NONE"])
                else:
                    print("skipping over ", name, "because we haven't verified it")

    except Exception as e:
        print(e)
