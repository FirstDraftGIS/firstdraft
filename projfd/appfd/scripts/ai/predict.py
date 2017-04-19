from ai_shared import *
from appfd.models import Order, Feature, FeaturePlace
from collections import Counter
from datetime import datetime
from decimal import Decimal
from django.db import connection
from numpy import array, float64, int64, ndarray, mean
from numpy import bool as numpy_bool
from os import listdir
from os.path import dirname, realpath
from pandas import DataFrame, read_csv
from random import choice, shuffle
from shutil import rmtree
from sklearn import datasets, metrics
import stepper
import tensorflow as tf
from tensorflow import constant, SparseTensor, Graph, Session
from tensorflow.contrib.learn.python.learn import DNNLinearCombinedClassifier, LinearClassifier
from tempfile import mkdtemp

PATH_TO_DIRECTORY_OF_THIS_FILE = dirname(realpath(__file__))
PATH_TO_DIRECTORY_OF_INPUT_DATA = PATH_TO_DIRECTORY_OF_THIS_FILE + "/data/input"
MODEL_DIR = PATH_TO_DIRECTORY_OF_THIS_FILE + "/classifier"

# pass column names into stepper
stepper.CATEGORICAL_COLUMNS = CATEGORICAL_COLUMNS
stepper.CONTINUOUS_COLUMNS = CONTINUOUS_COLUMNS
stepper.LABEL_COLUMN = LABEL_COLUMN
stepper.COLUMNS = COLUMNS

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

def run(geoentities, debug=True):

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

            if hasattr(geoentity, "cluster_frequency"):
                df['cluster_frequency'].append(geoentity.cluster_frequency or 0)
            else:
                df['cluster_frequency'].append(0)

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
            df['is_notable'].append(str(bool(geoentity.notability)))


            if hasattr(geoentity, "median_distance"):
                df['median_distance'].append(geoentity.median_distance_from_all_other_points)
            else:
                df['median_distance'].append(0)

            if hasattr(geoentity, "notability"):
                df['notability'].append(geoentity.notability or 0)
            else:
                df['notability'].append(0)


            if hasattr(geoentity, "matches_topic"):
                df['matches_topic'].append(str(geoentity.matches_topic or "False"))
            else:
                df['matches_topic'].append("False")
            df['population'].append(geoentity.population)
            df['popularity'].append(geoentity.popularity)

        duration = (datetime.now() - start_df).total_seconds()
        if duration < 60:
            print "populating df took", duration, "seconds"
        else:
            print "populating df took", float(duration) / 60, "minutes"

        def step():
            return stepper.step(df)

        for index, row in enumerate(classifier.predict_proba(input_fn=step)):
            geoentities[index].probability = row[1]

        print "predict.run took", (datetime.now() - start).total_seconds(), "seconds"

    except Exception as e:
        fail("EXCPETION in scripts.ai.predict.run: " + str(e))
