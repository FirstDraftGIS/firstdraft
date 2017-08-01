from ai_shared import *
from appfd.models import Feature, FeaturePlace, Place, Wikipedia
from datetime import datetime
from django.db import connection
from django.db.migrations.loader import MigrationLoader
from numpy import median
from os.path import dirname, join, realpath
import pickle
import stepper
from random import choice, random, randint, shuffle
from shutil import rmtree
from tensorflow.contrib.learn.python.learn import LinearClassifier, DNNLinearCombinedClassifier
import tensorflow as tf

PATH_TO_DIRECTORY_OF_THIS_FILE = dirname(realpath(__file__))
MODELS_DIR = PATH_TO_DIRECTORY_OF_THIS_FILE + "/classifiers/"

if len(MigrationLoader(connection, ignore_no_migrations=True).applied_migrations) > 0:
    # pass column names into stepper
    stepper.CATEGORICAL_COLUMNS = CATEGORICAL_COLUMNS
    stepper.CONTINUOUS_COLUMNS = CONTINUOUS_COLUMNS
    stepper.LABEL_COLUMN = LABEL_COLUMN
    stepper.COLUMNS = COLUMNS

def train_classifier(name, d):

    try:

        print "starting train_classifier with", name


        start = datetime.now()

        path_to_model = MODELS_DIR + name

        rmtree(path_to_model, ignore_errors=True)

        if "include_these_columns" in d:
            print "include_these_columns:", d["include_these_columns"]
            print "column_names:", [column.name for column in wide_columns]
            #raw_input('paused')
            linear_feature_columns = [ column for column in wide_columns if column.name in d['include_these_columns'] ]

            
        elif "exclude_these_columns" in d:
            linear_feature_columns = [ column for column in wide_columns if column.name not in d['exclude_these_columns'] ]
        else:
            linear_feature_columns = wide_columns

        print "linear_feature_columns:", len(linear_feature_columns)

        print "creating classifier"
        classifier = DNNLinearCombinedClassifier(
            fix_global_step_increment_bug=True,
            linear_feature_columns=linear_feature_columns,
            model_dir=path_to_model,
            n_classes=2,
            dnn_feature_columns=deep_columns,
            dnn_hidden_units=[100,50]
        )
        print "classifier:", type(classifier)

        features = d['features']
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

        """
        if debug:
            #print "\n\n\n\nXXXset of favor_local and mathces_end_user_timezone pairs:", set(zip(df_train['favor_local'], df_train['matches_end_user_timezone']))
            df_train['favor_local'] = ["False"] * len(df_train['favor_local'])
            df_train['matches_end_user_timezone'] = ["True"] * len(df_train['matches_end_user_timezone'])
        """
            
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

        columns = dict([(col.name, col) for col in classifier._feature_columns])
        print "columns:", columns.keys()
        #raw_input('paused')
        weights_to_pickle = {}
        for variable_name in variable_names:
            #if "weights" in variable_name:
            print "variable_name:", variable_name
            if variable_name.endswith("weight") or variable_name.endswith("weights"):
                print "\t- passes test"
                column_name = variable_name.split("/")[-2]
                print "\t- column_name:", column_name
                if column_name in columns:
                    print "\t- column_name in columns"
                    weights = classifier.get_variable_value(variable_name)
                    weights_to_pickle[column_name] = {}
                    column = columns[column_name]
                    if hasattr(column, "lookup_config"): # normal sparse column w keys
                        keys = column.lookup_config.keys
                        for index, key in enumerate(keys):
                            print "\t\t-", key, ":", weights[index]
                            weights_to_pickle[column_name][key] = float(weights[index][0])
                    elif hasattr(column, "columns"): # crossed column
                        col1, col2 = column.columns
                        index_in_weights = 0
                        for key1 in list(col1.lookup_config.keys) + ["UNFOUND"]:
                            for key2 in list(col2.lookup_config.keys) + ["UNFOUND"]:
                                crossed_key = key1 + " x " + key2
                                value = float(weights[index_in_weights])
                                print "\t\t-", crossed_key, ":", value
                                weights_to_pickle[crossed_key] = value
                                index_in_weights += 1

        #print "weights to pickle:", weights_to_pickle
        path_to_pickled_weights = join(PATH_TO_DIRECTORY_OF_THIS_FILE, "weights.pickle")
        print "path_to_pickled_weights:", path_to_pickled_weights
        with open(path_to_pickled_weights, "wb") as f:
            pickle.dump(weights_to_pickle, f)
        print "pickled"

        print "took", ((datetime.now() - start).total_seconds() / 60), "minutes to train " + name

        return classifier

    except Exception as e:

        print "CAUGHT EXCEPTION in train_classifier:", e


def run(fake_importance_data=True, debug=True):
    try:

        start = datetime.now()

        print "starting appbkto.scripts.predict.train"
        connection.close()
        featuredict = {
            'global': {
                'exclude_these_columns': exclude_these_columns_in_global,
                'features': []
            },
            'local': {
                'include_these_columns': include_these_columns_in_local,
                'features': []
            }
        }
        featuredict['global']['features'] += list(Feature.objects.filter(verified=True).values("id","featureplace__id","featureplace__place__admin_level","featureplace__correct","featureplace__place_id","featureplace__cluster_frequency","featureplace__place__country_code","featureplace__country_rank","featureplace__place__mpoly","featureplace__place__pcode","featureplace__popularity","featureplace__place__population","featureplace__median_distance","featureplace__place__topic_id","topic_id","featureplace__place__feature_code", "featureplace__place__feature_class","featureplace__place__wikipedia__charcount","featureplace__place__wikipedia__importance", "featureplace__place__timezone", "order__end_user_timezone"))

        for feature in featuredict['global']['features']:
            feature["featureplace__place__country_code"] = str(feature["featureplace__place__country_code"] or "None").upper()

        if fake_importance_data:

            fps = FeaturePlace.objects.exclude(country_rank=None).values_list("country_rank", flat=True)
            avg_country_rank_correct = median(list(fps.filter(correct=True)) or [5])
            avg_country_rank_incorrect = median(list(fps.filter(correct=False)) or [34])
            print "avg_country_rank_correct:", avg_country_rank_correct
            print "avg_country_rank_incorrect:", avg_country_rank_incorrect

            fps = FeaturePlace.objects.values_list("popularity", flat=True)
            avg_popularity_correct = median(list(fps.filter(correct=True)) or [3])
            avg_popularity_incorrect = median(list(fps.filter(correct=False)) or [-4])
            print "avg_popularity_correct:", avg_popularity_correct
            print "avg_popularity_incorrect:", avg_popularity_incorrect

            median_distances = FeaturePlace.objects.values_list("median_distance", flat=True)
            avg_median_distance_correct = median(list(median_distances.filter(correct=True)) or [70])
            avg_median_distance_incorrect = median(list(median_distances.filter(correct=False)) or [70])
            print "avg_median_distance_correct:", avg_median_distance_correct
            print "avg_median_distance_incorrect:", avg_median_distance_incorrect

            # iterate through highly important 
            for w in Wikipedia.objects.exclude(importance=None).order_by("-importance")[5e2:6e2].values("place_id", "place__name"):

                feature_id = randint(0, 100000)

                correct_place_id = w["place_id"]
                place__name = w["place__name"]
                for d in Place.objects.filter(name=place__name).values("admin_level", "country_code", "feature_class", "feature_code", "id", "mpoly", "pcode", "population", "topic_id", "wikipedia__charcount", "wikipedia__importance", "timezone"):
                    correct = d['id'] == correct_place_id
                    #print "correct:", correct
                    fake_feature = {
                        "id": feature_id,
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
                        "featureplace__median_distance": 50 if correct else 75,
                        "featureplace__place__topic_id": d['topic_id'],
                        "topic_id": None,
                        "featureplace__place__feature_code": str(d['feature_code']).upper(),
                        "featureplace__place__feature_class": str(d['feature_class']).upper(),
                        "featureplace__place__wikipedia__charcount": d['wikipedia__charcount'],
                        "featureplace__place__wikipedia__importance": d['wikipedia__importance'],
                        "featureplace__place__timezone": d['timezone'],
                        "order__end_user_timezone": None
                    }
                    featuredict['global']['features'].append(fake_feature)

            # iterate through less important places
            # so learns importance of matches_end_user_timezone when deciding between different unimportant places
            count_of_more_important_places = 0
            for w in Wikipedia.objects.exclude(importance=None).exclude(place__admin_level=None).order_by("importance")[:1e5].values("place_id", "place__name"):

                if count_of_more_important_places >= 5:
                    break
                more_important_place = Place.objects.filter(name=w['place__name'], wikipedia__importance__gte=0.75).order_by("-wikipedia__importance").first()
                if more_important_place:
                    print "more_important_place", more_important_place.name
                    correct_place_id = more_important_place.id
                    count_of_more_important_places += 1
                else:
                    correct_place_id = w["place_id"]
                    if len(featuredict['local']['features']) > 1000:
                        continue


                place__name = w["place__name"]
                found_correct = False
                for d in Place.objects.filter(name=place__name).values("admin_level", "country_code", "feature_class", "feature_code", "id", "mpoly", "pcode", "population", "topic_id", "wikipedia__charcount", "wikipedia__importance", "timezone"):
                    if not found_correct and d['id'] != correct_place_id:
                        correct = True
                        found_correct = True
                    fake_feature = {
                        "id": -1,
                        "featureplace__id": -1,
                        "featureplace__place__admin_level": d['admin_level'],
                        "featureplace__correct": correct,
                        "featureplace__place_id": d['id'],
                        "featureplace__cluster_frequency": 0,
                        "featureplace__place__country_code": d['country_code'],
                        "featureplace__country_rank": avg_country_rank_correct if correct else avg_country_rank_incorrect,
                        "featureplace__place__mpoly": d['mpoly'],
                        "featureplace__place__pcode": d['pcode'],
                        "featureplace__popularity": avg_popularity_correct if correct else avg_popularity_incorrect,
                        "featureplace__place__population": None,
                        "featureplace__median_distance": 50 if correct else 75,
                        "featureplace__place__topic_id": None,
                        "topic_id": None,
                        "featureplace__place__feature_code": d['feature_code'],
                        "featureplace__place__feature_class": d['feature_class'],
                        "featureplace__place__wikipedia__charcount": d['wikipedia__charcount'],
                        "featureplace__place__wikipedia__importance": d['wikipedia__importance'],
                        "featureplace__place__timezone": d['timezone'],
                        "order__end_user_timezone": d['timezone'] if correct else choice(time_zones)
                    }
                    featuredict['local']['features'].append(fake_feature)

        classifiers = {}
        for name, d  in featuredict.items():
            classifiers[name] = train_classifier(name, d)

        return classifiers

    except Exception as e:
        print "EXCEPTION in ai.train: " + str(e)
        raise(e)
