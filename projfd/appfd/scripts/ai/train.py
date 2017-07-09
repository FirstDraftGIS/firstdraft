from ai_shared import *
from appfd.models import Feature, FeaturePlace, Place, Wikipedia
from datetime import datetime
from django.db import connection
from numpy import median
from os.path import dirname, join, realpath
import pickle
import stepper
from random import choice, random, shuffle
from shutil import rmtree
from tensorflow.contrib.learn.python.learn import LinearClassifier, DNNLinearCombinedClassifier
import tensorflow as tf

PATH_TO_DIRECTORY_OF_THIS_FILE = dirname(realpath(__file__))
MODEL_DIR = PATH_TO_DIRECTORY_OF_THIS_FILE + "/classifier"

# pass column names into stepper
stepper.CATEGORICAL_COLUMNS = CATEGORICAL_COLUMNS
stepper.CONTINUOUS_COLUMNS = CONTINUOUS_COLUMNS
stepper.LABEL_COLUMN = LABEL_COLUMN
stepper.COLUMNS = COLUMNS

def run(fake_importance_data=False):
    try:

        start = datetime.now()

        print "starting appbkto.scripts.predict.train"
        connection.close()
        features = list(Feature.objects.filter(verified=True).values("id","featureplace__id","featureplace__place__admin_level","featureplace__correct","featureplace__place_id","featureplace__cluster_frequency","featureplace__place__country_code","featureplace__country_rank","featureplace__place__mpoly","featureplace__place__pcode","featureplace__popularity","featureplace__place__population","featureplace__median_distance","featureplace__place__topic_id","topic_id","featureplace__place__feature_code", "featureplace__place__feature_class","featureplace__place__wikipedia__charcount","featureplace__place__wikipedia__importance", "featureplace__place__timezone", "order__end_user_timezone"))
        print "features:", type(features), len(features)

        for feature in features:
            feature["featureplace__place__country_code"] = str(feature["featureplace__place__country_code"] or "None").upper()

        if fake_importance_data:

            fps = FeaturePlace.objects.exclude(country_rank=None).values_list("country_rank", flat=True)
            avg_country_rank_correct = median(list(fps.filter(correct=True)))
            avg_country_rank_incorrect = median(list(fps.filter(correct=False)))

            fps = FeaturePlace.objects.values_list("popularity", flat=True)
            avg_popularity_correct = median(list(fps.filter(correct=True)))
            avg_popularity_incorrect = median(list(fps.filter(correct=False)))

            median_distances = FeaturePlace.objects.values_list("median_distance", flat=True)
            avg_median_distance_correct = median(list(median_distances.filter(correct=True)))
            avg_median_distance_incorrect = median(list(median_distances.filter(correct=False)))

            for w in Wikipedia.objects.exclude(importance=None).exclude(place__admin_level=None).order_by("-importance")[:10].values("place_id", "place__name"):
                correct_place_id = w["place_id"]
                place__name = w["place__name"]
                for d in Place.objects.filter(name=place__name).values("admin_level", "country_code", "feature_class", "feature_code", "id", "mpoly", "pcode", "population", "topic_id", "wikipedia__charcount", "wikipedia__importance", "timezone"):
                    correct = d['id'] == correct_place_id
                    #print "correct:", correct
                    fake_feature = {
                        "id": -1,
                        "featureplace__id": -1,
                        "featureplace__place__admin_level": d['admin_level'],
                        "featureplace__correct": correct,
                        "featureplace__place_id": d['id'],
                        "featureplace__cluster_frequency": 0,
                        "featureplace__place__country_code": str(d['country_code']).upper(),
                        "featureplace__country_rank": avg_country_rank_correct if correct else avg_country_rank_incorrect,
                        "featureplace__place__mpoly": d['mpoly'],
                        "featureplace__place__pcode": d['pcode'],
                        "featureplace__popularity": avg_popularity_correct if correct else avg_popularity_incorrect,
                        "featureplace__place__population": d['population'],
                        "featureplace__median_distance": avg_median_distance_correct if correct else avg_median_distance_incorrect,
                        "featureplace__place__topic_id": d['topic_id'],
                        "topic_id": None,
                        "featureplace__place__feature_code": str(d['feature_code']).upper(),
                        "featureplace__place__feature_class": str(d['feature_class']).upper(),
                        "featureplace__place__wikipedia__charcount": d['wikipedia__charcount'],
                        "featureplace__place__wikipedia__importance": d['wikipedia__importance'],
                        "featureplace__place__timezone": d['timezone'],
                        "order__end_user_timezone": d['timezone'] if random() > 0.1 else ""
                    }
                    features.append(fake_feature)

            print "features with fake data", len(features)
        rmtree(MODEL_DIR, ignore_errors=True)

        print "creating classifier"
        #"""
        classifier = DNNLinearCombinedClassifier(
            fix_global_step_increment_bug=True,
            linear_feature_columns=wide_columns,
            model_dir=MODEL_DIR,
            n_classes=2,
            dnn_feature_columns=deep_columns,
            dnn_hidden_units=[100,50]
        )
        print "dir:", dir(classifier)
        # no longer variable
        #print "_linear_model:", classifier._linear_model
        #"""
        #classifier = LinearClassifier(feature_columns=wide_columns, model_dir=MODEL_DIR)
        print "classifier:", classifier

        number_of_features = len(features)

        print "training with real data"

        print "shuffle the features"
        shuffle(features)

        features_for_training, features_for_testing = halve(features)
        print "cut the features in half for training and testing"
        df_train = get_df_from_features(features_for_training)
        print "df_train:", type(df_train)
        print "len(feauters_for_training):", len(features_for_training)
        print "len(feauters_for_testing):", len(features_for_testing)
        df_test = get_df_from_features(features_for_testing)

        #for column_name in COLUMNS:
        #    print column_name, "\t", [v for v in df_train[column_name] if isinstance(v, type(None)) or isinstance(v, list)]

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

        #trainable_variables = tf.trainable_variables()
        #print "trainable_variables:", trainable_variables
        print "printing weights"
        variable_names = classifier.get_variable_names()
        print "variable_names:", variable_names

        print_these_variables = [
            "admin_level",
            "country_code",
            "edit_distance",
            "feature_class",
            "feature_code",
            "has_mpoly",
            "has_pcode",
            "is_country",
            "is_highest_population",
            "is_lowest_admin_level",
            "is_notable"
        ]

        weights_to_pickle = {}
        for variable_name in variable_names:
            #if "weights" in variable_name:
            print "variable_name:", variable_name
            if variable_name.endswith("/weights") and any(n in variable_name for n in print_these_variables) and "embedding" not in variable_name and "BUCKETIZED" not in variable_name and "_X_" not in variable_name:
                print "variable_name:", variable_name
                weights = classifier.get_variable_value(variable_name)
                column_name = variable_name.split("/")[-2]
                weights_to_pickle[column_name] = {}
                print "\n\n", column_name, ":"
                keys = globals()[column_name].lookup_config.keys
                for index, key in enumerate(keys):
                    #matched[key] = weights[index]
                    print key, ":", weights[index]
                    weights_to_pickle[column_name][key] = float(weights[index][0])

        print "weights to pickle:", weights_to_pickle
        path_to_pickled_weights = join(PATH_TO_DIRECTORY_OF_THIS_FILE, "weights.pickle")
        print "path_to_pickled_weights:", path_to_pickled_weights
        with open(path_to_pickled_weights, "wb") as f:
            pickle.dump(weights_to_pickle, f)
        print "pickled"

        print "took", ((datetime.now() - start).total_seconds() / 60), "minutes to train"

        return classifier

    except Exception as e:
        print "EXCEPTION in ai.train: " + str(e)
        raise(e)
