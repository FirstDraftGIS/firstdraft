from appfd.models import Order, Feature
from collections import Counter
from datetime import datetime
from decimal import Decimal
from django.db import connection
from numpy import array, ndarray
from os.path import dirname, realpath
from pandas import DataFrame
from random import choice
from sklearn import datasets, metrics
import tensorflow as tf
from tensorflow import constant, SparseTensor, Graph, Session
#from tensorflow.contrib.learn import LinearClassifier
from tensorflow.contrib.learn.python.learn import LinearClassifier
from tensorflow.contrib.layers import sparse_column_with_keys, sparse_column_with_hash_bucket, real_valued_column
from tempfile import mkdtemp

CATEGORICAL_COLUMNS = ["admin_level", "country_code", "has_pcode"]
CONTINUOUS_COLUMNS = ["edit_distance", "median_distance"]
LABEL_COLUMN = "correct"

global trained
trained = False

def input_fn(df):
    """Input builder function."""
    print("Creates a dictionary mapping from each continuous feature column name (k) to the values of that column stored in a constant Tensor.")
    continuous_cols = {}
    for k in CONTINUOUS_COLUMNS:
        print "K:", k
        #print "values:", type(df[k].values[0]), df[k].values[:5]
        continuous_cols[k] = constant(df[k].values, dtype=tf.float32)
        print continuous_cols[k]

    #continuous_cols['median_distance'] = constant(df[k].values, dtype=tf.float32)

    print("Creates a dictionary mapping from each categorical feature column name (k) to the values of that column stored in a tf.SparseTensor.")
    categorical_cols = {}
    for k in CATEGORICAL_COLUMNS:
        print "k:", k
        categorical_cols[k] = SparseTensor(
            indices=[[i, 0] for i in range(df[k].size)],
            values=df[k].values,
            shape=[df[k].size, 1])
        print "SparseTensor:", categorical_cols[k]
    # Merges the two dictionaries into one.
    feature_cols = dict(continuous_cols)
    feature_cols.update(categorical_cols)
    # Converts the label column into a constant Tensor.
    label = constant(df[LABEL_COLUMN].values)
    # Returns the feature columns and the label.
    return feature_cols, label

def train():
    try:
        global classifier
        global trained

        start = datetime.now()

        columns = ["admin_level","country_code", "edit_distance", "has_pcode","median_distance","correct"]
        df_train = DataFrame(columns=columns)
        df_test = DataFrame(columns=columns)

        print "starting appbkto.scripts.predict.train"
        connection.close()
        features = Feature.objects.values("featureplace__place__admin_level","featureplace__correct","featureplace__place__country_code","featureplace__place__pcode","featureplace__median_distance")
        print "features:", type(features), len(features)

        #country_name .. will make sure to weight against us because so popular make cross hatch column with country_count
        admin_level = sparse_column_with_keys(column_name="admin_level", keys=["None","0","1","2","3","4","5","6"]) # I've never seen admin 6, but you never know!
        edit_distance = real_valued_column("edit_distance")
        median_distance = real_valued_column("median_distance")
        population = real_valued_column("population")
        has_pcode = sparse_column_with_keys(column_name="has_pcode", keys=[True, False])
        has_mpoly = sparse_column_with_keys(column_name="has_mpoly", keys=[True, False])
        country_code = sparse_column_with_hash_bucket("country_code", hash_bucket_size=500)
        place_id = sparse_column_with_hash_bucket("country_code", hash_bucket_size=20000000)
        geoname_id = sparse_column_with_hash_bucket("country_code", hash_bucket_size=20000000)
        
        #number_of_other_points_in_country = sparse_column_with_hash_bucket("number_of_other_points_in_country", hash_bucket_size=1000)
        #number_of_other_points_in_admin1 = sparse_column_with_hash_bucket("number_of_other_points_in_admin1", hash_bucket_size=1000)
        #number_of_other_points_in_admin2 = sparse_column_with_hash_bucket("number_of_other_points_in_admin2", hash_bucket_size=1000)
        #feature_columns = {"country_code": [], "has_pcode":[], "has_mpoly":[]}
        feature_columns = [admin_level, country_code, edit_distance, median_distance]
        print "feature_columns:", feature_columns
        path_to_directory_of_this_file = dirname(realpath(__file__))
        #model_dir = path_to_directory_of_this_file + "/classifier"
        #classifier = LinearClassifier(feature_columns, model_dir=model_dir)
        classifier = LinearClassifier(feature_columns)
        print "classifier:", classifier
 
        for index, feature in enumerate(features):
            df_train['admin_level'].set_value(index, str(feature['featureplace__place__admin_level'] or "None"))
            df_train['country_code'].set_value(index, feature['featureplace__place__country_code'] or "None") 
            df_train['has_pcode'].set_value(index, feature['featureplace__place__pcode'] not in ["", None, False]) 
            df_train['edit_distance'].set_value(index, 0)
            df_train['median_distance'].set_value(index, feature['featureplace__median_distance'] or 9999 )
            df_train['correct'].set_value(index, 1)

        print("add in dummy data")

        # correct
        for i in range(len(features), 10000):
            df_train['admin_level'].set_value(i, choice(["None","None","0"]))
            df_train['country_code'].set_value(i, "None")
            df_train['edit_distance'].set_value(i, choice([0,0,0,1,2]))
            df_train['median_distance'].set_value(i, choice(range(19,100)))
            df_train['has_pcode'].set_value(i, choice([True,False,False]))
            df_train['correct'].set_value(i, 1)

        # incorrect
        for i in range(len(features)+10000, 10000):
            df_train['admin_level'].set_value(i, choice(["None","None","None","None","None","None","1","2","3","4"]))
            df_train['country_code'].set_value(i, "None")
            df_train['edit_distance'].set_value(i, choice([0,1,1,2,2]))
            df_train['median_distance'].set_value(i, choice(range(100,200)))
            df_train['has_pcode'].set_value(i, False)
            df_train['correct'].set_value(i, 0)

        print "fitting"
        classifier.fit(input_fn=lambda: input_fn(df_train), steps=1)
        print "\nfitted"
        results = classifier.evaluate(input_fn=lambda: input_fn(df_train), steps=1)
        for key in sorted(results):
            print("%s: %s" % (key, results[key]))

        #print "weights:", classifier.weights_

        trained = True

        print "took", (datetime.now() - start).total_seconds(), "seconds to train"

    except Exception as e:
        print e
        exit()

def run(geoentities):

    try:
        print "starting ai.predict with"
        connection.close()
        if not trained:
            train()
        print "trained:", trained
        print "classifier:", classifier

        #columns = ["admin_level","country_code","country_rank","edit_distance","has_pcode","median_distance","place_id","population"]
        columns = ["admin_level", "country_code", "edit_distance", "has_pcode","median_distance", "correct"]
        df = DataFrame(columns=columns)
        for index, g in enumerate(geoentities):
            df['admin_level'].set_value(index, str(g.admin_level or "None"))
            df['country_code'].set_value(index, g.country_code or "UNKNOWN")
            #df['country_rank'].set_value(index, g.country_rank or -1)
            df['edit_distance'].set_value(index, g.edit_distance)
            df['has_pcode'].set_value(index, False)
            df['median_distance'].set_value(index, g.median_distance_from_all_other_points)
            #df['place_id'].set_value(index, g.place_id or -1)
            #df['population'].set_value(index, g.population or -1)

        print "df:", type(df)

        for index, row in enumerate(classifier.predict_proba(input_fn=lambda: input_fn(df))):
            geoentities[index].probability = row[1]

    except Exception as e:
        print e
        exit()
