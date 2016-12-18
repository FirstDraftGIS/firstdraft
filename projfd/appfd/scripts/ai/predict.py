from appfd.models import Order, Feature, FeaturePlace
from collections import Counter
from datetime import datetime
from decimal import Decimal
from django.db import connection
from numpy import array, float64, int64, ndarray
from numpy import bool as numpy_bool
from os import listdir
from os.path import dirname, realpath
from pandas import DataFrame, read_csv
from random import choice, shuffle
from shutil import rmtree
from sklearn import datasets, metrics
import tensorflow as tf
from tensorflow import constant, SparseTensor, Graph, Session
from tensorflow.contrib.learn.python.learn import DNNLinearCombinedClassifier, LinearClassifier
from tensorflow.contrib.layers import bucketized_column, crossed_column, embedding_column, sparse_column_with_keys, sparse_column_with_hash_bucket, real_valued_column
from tempfile import mkdtemp

PATH_TO_DIRECTORY_OF_THIS_FILE = dirname(realpath(__file__))
PATH_TO_DIRECTORY_OF_INPUT_DATA = PATH_TO_DIRECTORY_OF_THIS_FILE + "/data/input"
MODEL_DIR = PATH_TO_DIRECTORY_OF_THIS_FILE + "/classifier"

CATEGORICAL_COLUMNS = ["admin_level", "country_code", "edit_distance", "feature_class", "feature_code", "has_mpoly", "has_pcode", "is_country", "is_highest_population", "is_lowest_admin_level", "matches_topic"]
CONTINUOUS_COLUMNS = ["cluster_frequency", "country_rank", "median_distance", "population", "popularity"]
LABEL_COLUMN = "correct"
COLUMNS = sorted(CATEGORICAL_COLUMNS + CONTINUOUS_COLUMNS) + [LABEL_COLUMN]
print "COLUMNS:", COLUMNS


admin_level = sparse_column_with_keys(column_name="admin_level", keys=["None","0","1","2","3","4","5","6"]) # I've never seen admin 6, but you never know!
cluster_frequency = real_valued_column("cluster_frequency")
cluster_frequency_buckets = bucketized_column(cluster_frequency, boundaries=[0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1])
country_code = sparse_column_with_hash_bucket("country_code", hash_bucket_size=500)
country_rank = real_valued_column("country_rank")
edit_distance = sparse_column_with_keys(column_name="edit_distance", keys=["0", "1", "2"])
feature_class = sparse_column_with_hash_bucket("feature_class", hash_bucket_size=100)
feature_code = sparse_column_with_hash_bucket("feature_code", hash_bucket_size=1000)
country_code = sparse_column_with_hash_bucket("country_code", hash_bucket_size=500)
has_pcode = sparse_column_with_keys(column_name="has_pcode", keys=["True", "False"])
has_mpoly = sparse_column_with_keys(column_name="has_mpoly", keys=["True", "False"])
is_country = sparse_column_with_keys(column_name="is_country", keys=["True", "False"])
is_lowest_admin_level = sparse_column_with_keys(column_name="is_lowest_admin_level", keys=["True", "False"])
is_highest_population = sparse_column_with_keys(column_name="is_highest_population", keys=["True", "False"])
matches_topic = sparse_column_with_keys(column_name="matches_topic", keys=["True", "False"])
median_distance = real_valued_column("median_distance")
median_distance_buckets = bucketized_column(median_distance, boundaries=[10,50,100,200,300])
population = real_valued_column("population")
population_buckets = bucketized_column(population, boundaries=[0, 1, 100, 1000, 10000, 100000, 1000000, 10000000, 100000000])
popularity = real_valued_column("popularity")
admin_level_x_median_distance = crossed_column([admin_level, median_distance_buckets], hash_bucket_size=int(1e4))
admin_level_x_cluster_frequency = crossed_column([admin_level, cluster_frequency_buckets], hash_bucket_size=int(1e4))
admin_level_x_country_code = crossed_column([admin_level, country_code], hash_bucket_size=int(1e4))
        
#number_of_other_points_in_country = sparse_column_with_hash_bucket("number_of_other_points_in_country", hash_bucket_size=1000)
#number_of_other_points_in_admin1 = sparse_column_with_hash_bucket("number_of_other_points_in_admin1", hash_bucket_size=1000)
#number_of_other_points_in_admin2 = sparse_column_with_hash_bucket("number_of_other_points_in_admin2", hash_bucket_size=1000)
#feature_columns = [admin_level, cluster_frequency_buckets, country_code, country_rank, edit_distance, is_lowest_admin_level, has_mpoly, has_pcode, matches_topic, median_distance, median_distance_buckets, population_buckets, popularity, admin_level_x_cluster_frequency, admin_level_x_country_code, admin_level_x_median_distance]
#print "feature_columns:", feature_columns
wide_columns = [admin_level, cluster_frequency_buckets, country_code, country_rank, edit_distance, is_country, is_highest_population, is_lowest_admin_level, has_mpoly, has_pcode, matches_topic, median_distance, median_distance_buckets, population_buckets, popularity, admin_level_x_cluster_frequency, admin_level_x_country_code, admin_level_x_median_distance]
deep_columns = [
    embedding_column(admin_level, dimension=8),
    cluster_frequency,
    cluster_frequency_buckets,
    embedding_column(country_code, dimension=8),
    country_rank,
    embedding_column(has_mpoly, dimension=8),
    embedding_column(has_pcode, dimension=8),
    embedding_column(is_country, dimension=8),
    embedding_column(is_lowest_admin_level, dimension=8),
    embedding_column(is_highest_population, dimension=8),
    median_distance_buckets,
    population_buckets,
    popularity
]


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

def halve(iterable):
    half = len(iterable) / 2
    return iterable[:half], iterable[half:]

def info(string):
    print(bcolors.OKBLUE + string + bcolors.ENDC)

def input_fn(d):
  try:

    for column_name in COLUMNS:
        if column_name not in d:
            raise Exception(column_name + " not in d")

    num_rows = len(d['admin_level'])
    feature_cols = {}
    for k in CONTINUOUS_COLUMNS:
        feature_cols[k] = constant(d[k], dtype=tf.float32)

    for k in CATEGORICAL_COLUMNS:
        feature_cols[k] = SparseTensor(
            indices=[[i, 0] for i in range(num_rows)],
            values=d[k],
            shape=[num_rows, 1])
    label = constant(d[LABEL_COLUMN])


    return feature_cols, label
  except Exception as e:
    fail("EXCEPTION in input_fn: " + str(e))


def get_fake_df():
    return dict([(k, []) for k in COLUMNS])

def get_df_from_features(features):

    df = get_fake_df()
    add_features_to_df(df, features)
    return df

def add_features_to_df(df, features):

    # data frame for training
    for index, feature in enumerate(features):

        fid = feature['id']
        fpid = feature['featureplace__id']

        feature_admin_levels = set([f['featureplace__place__admin_level'] for f in features if f['featureplace__place__admin_level'] and f['id'] == fid])
        if feature_admin_levels:
            lowest_admin_level = min(feature_admin_levels)
        else:
            lowest_admin_level = -99

        population = feature['featureplace__place__population']
        is_highest_population = population and population == max([f['featureplace__place__population'] for f in features if f['id'] == fid]) or False

        place_id = feature['featureplace__place_id']
        admin_level = feature['featureplace__place__admin_level']
        df['admin_level'].append(str(admin_level or "None"))
        df['cluster_frequency'].append(feature['featureplace__cluster_frequency'] or 0)
        df['country_code'].append(feature['featureplace__place__country_code'] or "None") 
        df['country_rank'].append(feature['featureplace__country_rank'] or 999) 
        df['feature_class'].append(feature['featureplace__place__feature_class'] or "None") 
        df['feature_code'].append(feature['featureplace__place__feature_code'] or "None") 
        df['has_mpoly'].append(str(feature['featureplace__place__mpoly'] is not None))
        df['has_pcode'].append(str(feature['featureplace__place__pcode'] is not None)) 
        df['is_country'].append(str(admin_level == 0))
        df['is_lowest_admin_level'].append(str(lowest_admin_level == admin_level))
        df['is_highest_population'].append(str(is_highest_population))
        df['edit_distance'].append("0")
        df['median_distance'].append(feature['featureplace__median_distance'] or 9999 )
        df['matches_topic'].append(str(feature['topic_id'] == feature["featureplace__place__topic_id"]) if feature['topic_id'] else "False")
        df['population'].append(int(population or 0))
        df['popularity'].append(int(feature['featureplace__popularity'] or 0))
        df['correct'].append(1 if feature['featureplace__correct'] else 0)

def get_df_from_csv(path_to_csv):
    d = {}
    real_df = read_csv(path_to_csv, sep="\t")
    for column_name in real_df:
        # ignore columns we no longer use
        if column_name in COLUMNS:
            column = real_df[column_name]
            values = list(real_df[column_name].values)
            if column_name == "country_code":
                values = [unicode(v) for v in values]
            elif column_name == "edit_distance":
                values = [str(v) for v in values]
            elif column.dtype == numpy_bool:
                values = [str(v) for v in values]
            elif column.dtype == int64:
                values = [int(v) for v in values]
            elif column.dtype == float64:
                values = [float(v) for v in values]

            d[column_name] = values
    return d

def train():
    try:

        start = datetime.now()

        print "starting appbkto.scripts.predict.train"
        connection.close()
        features = list(Feature.objects.filter(verified=True).values("id","featureplace__id","featureplace__place__admin_level","featureplace__correct","featureplace__place_id","featureplace__cluster_frequency","featureplace__place__country_code","featureplace__country_rank","featureplace__place__mpoly","featureplace__place__pcode","featureplace__popularity","featureplace__place__population","featureplace__median_distance","featureplace__place__topic_id","topic_id","featureplace__place__feature_code", "featureplace__place__feature_class"))
        print "features:", type(features), len(features)

        rmtree(MODEL_DIR, ignore_errors=True)

        print "creating classifier"
        classifier = DNNLinearCombinedClassifier(
            model_dir=MODEL_DIR,
            linear_feature_columns=wide_columns,
            dnn_feature_columns=deep_columns,
            dnn_hidden_units=[100,50]
        )
        print "classifier:", classifier

        number_of_features = len(features)

        print "training with real data"

        print "shuffle the features"
        shuffle(features)

        features_for_training, features_for_testing = halve(features)
        df_train = get_df_from_features(features_for_training)
        print "len(feauters_for_training):", len(features_for_training)
        print "len(feauters_for_testing):", len(features_for_testing)
        df_test = get_df_from_features(features_for_testing)

        for filename in listdir(PATH_TO_DIRECTORY_OF_INPUT_DATA):
            print "filename for import :", filename
            if filename.endswith(".csv"):
                df = get_df_from_csv(PATH_TO_DIRECTORY_OF_INPUT_DATA + "/" + filename)
                for column_name in df:
                    column = df[column_name]
                    if type(df_train[column_name][0]) != type(column[0]):
                        print "mismatch type for ", column_name
                        print "type(df_train[column_name][0]):", type(df_train[column_name][0])

                    for_training, for_testing = halve(column)
                    print "len(for_testing):", len(for_testing)
                    if column_name in df_train:
                        df_train[column_name].extend(for_training)
                    else:
                        df_train[column_name] = for_training

                    if column_name in df_test:
                        df_test[column_name].extend(for_testing)
                    else:
                        df_test[column_name] = for_testing
 

        for column_name in COLUMNS:
            print column_name, "\t", [v for v in df_train[column_name] if isinstance(v, type(None)) or isinstance(v, list)]

        print "fitting"
        print "keys:", df_train.keys()
        try:
            classifier.fit(input_fn=lambda: input_fn(df_train), steps=200)
        except Exception as e:
            fail("EXCEPTION fitting model in scripts.ai.predict.train: " + str(e))
        print "\nfitted"
        results = classifier.evaluate(input_fn=lambda: input_fn(df_test), steps=10)
        for key in sorted(results):
            print("%s: %s" % (key, results[key]))

        print "took", ((datetime.now() - start).total_seconds() / 60), "minutes to train"

    except Exception as e:
        fail("EXCEPTION in ai.predict.train: " + str(e))
        raise(e)

def run(geoentities):

    try:

        print "starting ai.predict"
        connection.close()

        start = datetime.now()        

        classifier = DNNLinearCombinedClassifier(
            model_dir=MODEL_DIR,
            linear_feature_columns=wide_columns,
            dnn_feature_columns=deep_columns,
            dnn_hidden_units=[100,50]
        )
        print "classifier:", classifier

        print "creating the classifier took", (datetime.now() - start).total_seconds(), "seconds"

        df = get_fake_df()
        print "about to populate data frame for prediction"
        start_df = datetime.now()
        
        for index, geoentity in enumerate(geoentities):
            place_id = geoentity.place_id
            name = geoentity.target

	    feature_admin_levels = set([g.admin_level for g in geoentities if g.admin_level and g.target == name])
            if feature_admin_levels:
                lowest_admin_level = min(feature_admin_levels)
            else:
                lowest_admin_level = -99

            population = g.population
            is_highest_population = population and population == max([g.population for g in geoentities if g.target == name]) or False

            admin_level = geoentity.admin_level
            df['admin_level'].append(str(geoentity.admin_level or "None"))
            df['cluster_frequency'].append(geoentity.cluster_frequency or 0)
            df['country_code'].append(geoentity.country_code or "UNKNOWN")
            df['country_rank'].append(geoentity.country_rank or 999)
            df['edit_distance'].append(str(geoentity.edit_distance))
            df['feature_class'].append(str(geoentity.feature_class or "None"))
            df['feature_code'].append(str(geoentity.feature_code or "None"))
            df['has_mpoly'].append(str(geoentity.has_mpoly or False))
            df['has_pcode'].append(str(geoentity.has_pcode or False))
            df['is_country'].append(str(admin_level == 0))
            df['is_lowest_admin_level'].append(str(lowest_admin_level == g.admin_level))
            df['is_highest_population'].append(str(is_highest_population))
            df['median_distance'].append(geoentity.median_distance_from_all_other_points)
            df['matches_topic'].append(str(geoentity.matches_topic or "False"))
            df['population'].append(geoentity.population)
            df['popularity'].append(geoentity.popularity)

        print "populating df took", ((datetime.now() - start_df).total_seconds() / 60), "minutes"

        for index, row in enumerate(classifier.predict_proba(input_fn=lambda: input_fn(df))):
            geoentities[index].probability = row[1]

    except Exception as e:
        fail("EXCPETION in scripts.ai.predict.run: " + str(e))
