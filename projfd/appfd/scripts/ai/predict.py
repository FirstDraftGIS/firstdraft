from appfd.models import Order, Feature, FeaturePlace
from collections import Counter
from datetime import datetime
from decimal import Decimal
from django.db import connection
from numpy import array, ndarray
from os.path import dirname, realpath
from pandas import DataFrame
from random import choice, shuffle
from shutil import rmtree
from sklearn import datasets, metrics
import tensorflow as tf
from tensorflow import constant, SparseTensor, Graph, Session
from tensorflow.contrib.learn.python.learn import LinearClassifier
from tensorflow.contrib.layers import sparse_column_with_keys, sparse_column_with_hash_bucket, real_valued_column
from tempfile import mkdtemp

PATH_TO_DIRECTORY_OF_THIS_FILE = dirname(realpath(__file__))
MODEL_DIR = PATH_TO_DIRECTORY_OF_THIS_FILE + "/classifier"

CATEGORICAL_COLUMNS = ["admin_level", "country_code", "has_mpoly", "has_pcode", "matches_topic"]
CONTINUOUS_COLUMNS = ["cluster_frequency", "country_rank", "edit_distance", "median_distance", "population", "popularity"]
LABEL_COLUMN = "correct"
COLUMNS = sorted(CATEGORICAL_COLUMNS + CONTINUOUS_COLUMNS) + [LABEL_COLUMN]
print "COLUMNS:", COLUMNS


admin_level = sparse_column_with_keys(column_name="admin_level", keys=["None","0","1","2","3","4","5","6"]) # I've never seen admin 6, but you never know!
cluster_frequency = real_valued_column("cluster_frequency")
country_code = sparse_column_with_hash_bucket("country_code", hash_bucket_size=500)
country_rank = real_valued_column("country_rank")
edit_distance = real_valued_column("edit_distance")
geoname_id = sparse_column_with_hash_bucket("country_code", hash_bucket_size=20000000)
has_pcode = sparse_column_with_keys(column_name="has_pcode", keys=["True", "False"])
has_mpoly = sparse_column_with_keys(column_name="has_mpoly", keys=["True", "False"])
matches_topic = sparse_column_with_keys(column_name="matches_topic", keys=["True", "False"])
median_distance = real_valued_column("median_distance")
population = real_valued_column("population")
popularity = real_valued_column("popularity")
        
#number_of_other_points_in_country = sparse_column_with_hash_bucket("number_of_other_points_in_country", hash_bucket_size=1000)
#number_of_other_points_in_admin1 = sparse_column_with_hash_bucket("number_of_other_points_in_admin1", hash_bucket_size=1000)
#number_of_other_points_in_admin2 = sparse_column_with_hash_bucket("number_of_other_points_in_admin2", hash_bucket_size=1000)
feature_columns = [admin_level, cluster_frequency, country_code, country_rank, edit_distance, has_mpoly, has_pcode, median_distance, matches_topic, population, popularity]
print "feature_columns:", feature_columns

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def fail(string):
    print(bcolors.FAIL + string + bcolors.ENDC)

def info(string):
    print(bcolors.OKBLUE + string + bcolors.ENDC)

def input_fn(df):
  try:
    """Input builder function."""
    info("Creates a dictionary mapping from each continuous feature column name (k) to the values of that column stored in a constant Tensor.")
    continuous_cols = {}
    for k in CONTINUOUS_COLUMNS:
        print "K:", k
        #print "values:", type(df[k].values[0]), df[k].values[:5]
        continuous_cols[k] = constant(df[k].values, dtype=tf.float32)
        print continuous_cols[k]

    info("Creates a dictionary mapping from each categorical feature column name (k) to the values of that column stored in a tf.SparseTensor.")
    categorical_cols = {}
    for k in CATEGORICAL_COLUMNS:
        print "k:", k
        print "values:", type(df[k].values[0]), df[k].values[:5]
        categorical_cols[k] = SparseTensor(
            indices=[[i, 0] for i in range(df[k].size)],
            values=df[k].values,
            shape=[df[k].size, 1])
        print "SparseTensor:", categorical_cols[k]
    info("Merges the two dictionaries into one.")
    feature_cols = dict(continuous_cols)
    feature_cols.update(categorical_cols)
    info("Converts the label column into a constant Tensor.")
    label = constant(df[LABEL_COLUMN].values)
    info("Returns the feature columns and the label.")
    return feature_cols, label
  except Exception as e:
    fail("EXCEPTION in input_fn: " + str(e))

def train():
    try:

        start = datetime.now()

        df_train = DataFrame(columns=COLUMNS)
        df_test = DataFrame(columns=COLUMNS)

        print "starting appbkto.scripts.predict.train"
        connection.close()
        features = list(Feature.objects.filter(verified=True).values("featureplace__place__admin_level","featureplace__correct","featureplace__place_id","featureplace__cluster_frequency","featureplace__place__country_code","featureplace__country_rank","featureplace__place__mpoly","featureplace__place__pcode","featureplace__popularity","featureplace__place__population","featureplace__median_distance","featureplace__place__topic_id","topic_id"))
        print "features:", type(features), len(features)

        rmtree(MODEL_DIR, ignore_errors=True)

        print "creating classifier"
        classifier = LinearClassifier(feature_columns, model_dir=MODEL_DIR)
        print "classifier:", classifier
 

        number_of_features = len(features)

        try:

            print "training with real data"

            print "shuffle the features"
            shuffle(features)

            half = number_of_features / 2
            print "half is", half

            # data frame for training
            for index, feature in enumerate(features[:half]):
                place_id = feature['featureplace__place_id']
                df_train['admin_level'].set_value(index, str(feature['featureplace__place__admin_level'] or "None"))
                df_train['cluster_frequency'].set_value(index, feature['featureplace__cluster_frequency'] or 0)
                df_train['country_code'].set_value(index, feature['featureplace__place__country_code'] or "None") 
                df_train['country_rank'].set_value(index, feature['featureplace__country_rank'] or 999) 
                df_train['has_mpoly'].set_value(index, str(feature['featureplace__place__mpoly'] is not None))
                df_train['has_pcode'].set_value(index, str(feature['featureplace__place__pcode'] is not None)) 
                df_train['edit_distance'].set_value(index, 0)
                df_train['median_distance'].set_value(index, feature['featureplace__median_distance'] or 9999 )
                df_train['matches_topic'].set_value(index, str(feature['topic_id'] == feature["featureplace__place__topic_id"]) if feature['topic_id'] else "False")
                df_train['population'].set_value(index, int(feature['featureplace__place__population'] or 0))
                df_train['popularity'].set_value(index, int(feature['featureplace__popularity'] or 0))
                df_train['correct'].set_value(index, 1 if feature['featureplace__correct'] else 0)

            # data frame for testing
            for index, feature in enumerate(features[half:]):
                place_id = feature['featureplace__place_id']
                df_test['admin_level'].set_value(index, str(feature['featureplace__place__admin_level'] or "None"))
                df_test['cluster_frequency'].set_value(index, feature['featureplace__cluster_frequency'] or 0)
                df_test['country_code'].set_value(index, feature['featureplace__place__country_code'] or "None") 
                df_test['country_rank'].set_value(index, feature['featureplace__country_rank'] or 999) 
                df_test['has_mpoly'].set_value(index, str(feature['featureplace__place__mpoly'] is not None))
                df_test['has_pcode'].set_value(index, str(feature['featureplace__place__pcode'] is not None)) 
                df_test['edit_distance'].set_value(index, 0)
                df_test['median_distance'].set_value(index, feature['featureplace__median_distance'] or 9999 )
                df_test['matches_topic'].set_value(index, str(feature['topic_id'] == feature["featureplace__place__topic_id"]) if feature['topic_id'] else "False")
                df_test['population'].set_value(index, int(feature['featureplace__place__population'] or 0))
                df_test['popularity'].set_value(index, int(feature['featureplace__popularity'] or 0))
                df_test['correct'].set_value(index, 1 if feature['featureplace__correct'] else 0)

        except Exception as e:
            print e

        print("add in dummy data")

        print "fitting"
        try:
            classifier.fit(input_fn=lambda: input_fn(df_train), steps=10)
        except Exception as e:
            fail("EXCEPTION fitting model in scripts.ai.predict.train: " + str(e))
        print "\nfitted"
        results = classifier.evaluate(input_fn=lambda: input_fn(df_test), steps=10)
        for key in sorted(results):
            print("%s: %s" % (key, results[key]))

        weights = classifier.weights_
        #print "weights for", weights.keys()
        for key in weights:
            print key, ":", weights[key]

        print "took", (datetime.now() - start).total_seconds(), "seconds to train"

    except Exception as e:
        fail("EXCEPTION in ai.predict.train: " + str(e))

def run(geoentities):

    try:

        print "starting ai.predict"
        connection.close()

        start = datetime.now()        
        classifier = LinearClassifier(feature_columns, model_dir=MODEL_DIR)
        
        print "creating the classifier took", (datetime.now() - start).total_seconds(), "seconds"

        df = DataFrame(columns=COLUMNS)
        print "about to populate data frame for prediction"
        start_df = datetime.now()
        
        for index, g in enumerate(geoentities):
            place_id = g.place_id
            df['admin_level'].set_value(index, str(g.admin_level or "None"))
            df['cluster_frequency'].set_value(index, g.cluster_frequency or 0)
            df['country_code'].set_value(index, g.country_code or "UNKNOWN")
            df['country_rank'].set_value(index, g.country_rank or 999)
            df['edit_distance'].set_value(index, g.edit_distance)
            df['has_mpoly'].set_value(index, str(g.has_mpoly or False))
            df['has_pcode'].set_value(index, str(g.has_pcode or False))
            df['median_distance'].set_value(index, g.median_distance_from_all_other_points)
            df['matches_topic'].set_value(index, str(g.matches_topic or "False"))
            df['population'].set_value(index, g.population)
            df['popularity'].set_value(index, g.popularity)
        """
        admin_level = []
        cluster_frequency = []
        country_code = []
        country_rank = []
        edit_distance = []
        has_mpoly = []
        has_pcode = []
        median_distance = []
        matches_topic = []
        population = []
        popularity = []
         
        for g in geoentities:
            admin_level.append(str(g.admin_level))
            cluster_frequency.append(g.cluster_frequency or 0)
            country_code.append(str(g.country_code))
            country_rank.append(g.country_rank or 999)
            edit_distance.append(g.edit_distance)
            has_mpoly.append(str(g.has_mpoly or False))
            has_pcode.append(str(g.has_pcode or False))
            median_distance.append(g.median_distance_from_all_other_points)
            matches_topic.append(str(g.matches_topic or False))
            population.append(g.population or 0)
            popularity.append(FeaturePlace.objects.filter(correct=True, feature__verified=True, place_id=g.place_id).count())
        """
        
    

        print "populating df took", (datetime.now() - start_df).total_seconds(), "seconds"

        for index, row in enumerate(classifier.predict_proba(input_fn=lambda: input_fn(df))):
            geoentities[index].probability = row[1]

    except Exception as e:
        fail("EXCPETION in scripts.ai.predict.run: " + str(e))
