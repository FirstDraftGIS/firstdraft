from ai_shared import *
from appfd.models import Feature
from datetime import datetime
from django.db import connection
from os.path import dirname, realpath
import stepper
from random import choice, shuffle
from shutil import rmtree
from tensorflow.contrib.learn.python.learn import DNNLinearCombinedClassifier

PATH_TO_DIRECTORY_OF_THIS_FILE = dirname(realpath(__file__))
MODEL_DIR = PATH_TO_DIRECTORY_OF_THIS_FILE + "/classifier"

# pass column names into stepper
stepper.CATEGORICAL_COLUMNS = CATEGORICAL_COLUMNS
stepper.CONTINUOUS_COLUMNS = CONTINUOUS_COLUMNS
stepper.LABEL_COLUMN = LABEL_COLUMN
stepper.COLUMNS = COLUMNS

def run():
    try:

        start = datetime.now()

        print "starting appbkto.scripts.predict.train"
        connection.close()
        features = list(Feature.objects.filter(verified=True).values("id","featureplace__id","featureplace__place__admin_level","featureplace__correct","featureplace__place_id","featureplace__cluster_frequency","featureplace__place__country_code","featureplace__country_rank","featureplace__place__mpoly","featureplace__place__pcode","featureplace__popularity","featureplace__place__population","featureplace__median_distance","featureplace__place__topic_id","topic_id","featureplace__place__feature_code", "featureplace__place__feature_class", "featureplace__place__wikipedia__charcount"))
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
        print "cut the features in half for training and testing"
        df_train = get_df_from_features(features_for_training)
        print "len(feauters_for_training):", len(features_for_training)
        print "len(feauters_for_testing):", len(features_for_testing)
        df_test = get_df_from_features(features_for_testing)

        for column_name in COLUMNS:
            print column_name, "\t", [v for v in df_train[column_name] if isinstance(v, type(None)) or isinstance(v, list)]

        print "fitting"
        print "keys:", df_train.keys()
        try:
            classifier.fit(input_fn=lambda: stepper.step(df_train), steps=200)
        except Exception as e:
            print("EXCEPTION fitting model in scripts.ai.predict.train: " + str(e))
        print "\nfitted"
        results = classifier.evaluate(input_fn=lambda: stepper.step(df_test), steps=10)
        for key in sorted(results):
            print("%s: %s" % (key, results[key]))

        print "took", ((datetime.now() - start).total_seconds() / 60), "minutes to train"

    except Exception as e:
        print "EXCEPTION in ai.train: " + str(e)
        raise(e)
