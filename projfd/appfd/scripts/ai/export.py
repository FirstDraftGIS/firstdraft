from appfd.models import Feature
from appfd.scripts.ai.predict import get_df_from_features
from datetime import datetime
from os.path import dirname, realpath
from pandas import DataFrame

path_to_directory_of_this_file = dirname(realpath(__file__))

# used to create csv that other fdgis instances can read in to train their models
def run():
    try:
        print "starting export"

        features = list(Feature.objects.filter(verified=True).values("id","featureplace__id","featureplace__place__admin_level","featureplace__correct","featureplace__place_id","featureplace__cluster_frequency","featureplace__place__country_code","featureplace__country_rank","featureplace__place__mpoly","featureplace__place__pcode","featureplace__popularity","featureplace__place__population","featureplace__median_distance","featureplace__place__topic_id","topic_id","featureplace__place__feature_class", "featureplace__place__feature_code"))

        data = get_df_from_features(features)

        dataFrame = DataFrame(data=data)
        
        path_to_csv = path_to_directory_of_this_file + "/data/output/" + datetime.now().isoformat() + ".csv"
        dataFrame.to_csv(path_to_csv, sep="\t")

        print "saved data to ", path_to_csv

    except Exception as e:
        print e
