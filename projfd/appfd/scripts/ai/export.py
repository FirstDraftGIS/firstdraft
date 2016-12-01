from appfd.models import Feature
from appfd.scripts.ai.predict import get_df_from_features
from pandas import DataFrame

# used to create csv that other fdgis instances can read in to train their models
def run():
    try:
        print "starting export"

        features = list(Feature.objects.filter(verified=True).values("id","featureplace__id","featureplace__place__admin_level","featureplace__correct","featureplace__place_id","featureplace__cluster_frequency","featureplace__place__country_code","featureplace__country_rank","featureplace__place__mpoly","featureplace__place__pcode","featureplace__popularity","featureplace__place__population","featureplace__median_distance","featureplace__place__topic_id","topic_id"))

        data = get_df_from_features(features)

        dataFrame = DataFrame(data=data)
        
        path_to_csv = "/tmp/fdgis_data.txt"
        dataFrame.to_csv(path_to_csv, sep="\t")

    except Exception as e:
        print e
