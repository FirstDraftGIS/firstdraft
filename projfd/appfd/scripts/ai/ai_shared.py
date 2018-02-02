from appfd.models import Place
from django.db import connection
from django.db.migrations.loader import MigrationLoader
import georefdata
from os.path import dirname, join, realpath
from tensorflow.contrib.layers import bucketized_column, crossed_column, embedding_column, sparse_column_with_keys, sparse_column_with_hash_bucket, real_valued_column

PATH_TO_DIRECTORY_OF_THIS_FILE = dirname(realpath(__file__))
MODELS_DIR = PATH_TO_DIRECTORY_OF_THIS_FILE + "/classifiers/"

if len(MigrationLoader(connection, ignore_no_migrations=True).applied_migrations) > 0:

    cursor = connection.cursor()

    loose_index_scan = """
WITH RECURSIVE t AS (
    SELECT MIN({0}) AS {0} FROM appfd_place
    UNION ALL
    SELECT (SELECT MIN({0}) FROM appfd_place WHERE {0} > t.{0})
    FROM t WHERE t.{0} IS NOT NULL
)
SELECT {0} FROM t WHERE {0} IS NOT NULL
UNION ALL
SELECT NULL WHERE EXISTS(SELECT 1 FROM appfd_place WHERE {0} IS NULL);
"""


    CATEGORICAL_COLUMNS = ["country_code", "edit_distance", "favor_local", "feature_class", "feature_code", "has_mpoly", "has_pcode", "is_highest_population", "is_lowest_admin_level", "matches_end_user_timezone", "matches_topic", "is_important", "is_notable", "matches_end_user_timezone_X_is_most_important_in_timezone", "is_most_important_in_timezone"]
    CONTINUOUS_COLUMNS = ["country_rank", "median_distance", "notability", "popularity", "importance"]
    LABEL_COLUMN = "correct"
    COLUMNS = sorted(CATEGORICAL_COLUMNS + CONTINUOUS_COLUMNS) + [LABEL_COLUMN]


    #number_of_other_points_in_country = sparse_column_with_hash_bucket("number_of_other_points_in_country", hash_bucket_size=1000)
    #number_of_other_points_in_admin1 = sparse_column_with_hash_bucket("number_of_other_points_in_admin1", hash_bucket_size=1000)
    #number_of_other_points_in_admin2 = sparse_column_with_hash_bucket("number_of_other_points_in_admin2", hash_bucket_size=1000)

    #admin_level = sparse_column_with_keys(column_name="admin_level", keys=["None","0","1","2","3","4","5","6"]) # I've never seen admin 6, but you never know!
    #cluster_frequency = real_valued_column("cluster_frequency")
    #cluster_frequency_buckets = bucketized_column(cluster_frequency, boundaries=[0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1])

    country_codes = georefdata.get_country_codes()
    country_code = sparse_column_with_keys("country_code", keys=country_codes)

    country_rank = real_valued_column("country_rank")
    edit_distance = sparse_column_with_keys(column_name="edit_distance", keys=["0", "1", "2"])

    favor_local = sparse_column_with_keys(column_name="favor_local", keys=["True", "False", "Unknown"])

    feature_classes = georefdata.get_geonames_feature_classes()
    feature_class = sparse_column_with_keys("feature_class", keys=feature_classes)

    feature_codes = georefdata.get_geonames_feature_codes()
    feature_code = sparse_column_with_keys("feature_code", keys=feature_codes)

    has_pcode = sparse_column_with_keys(column_name="has_pcode", keys=["True", "False"])
    has_mpoly = sparse_column_with_keys(column_name="has_mpoly", keys=["True", "False"])
    importance = real_valued_column("importance")
    #is_country = sparse_column_with_keys(column_name="is_country", keys=["True", "False"])
    is_lowest_admin_level = sparse_column_with_keys(column_name="is_lowest_admin_level", keys=["True", "False"])
    is_highest_population = sparse_column_with_keys(column_name="is_highest_population", keys=["True", "False"])
    is_notable = sparse_column_with_keys(column_name="is_notable", keys=["True", "False"]) # does it appear in Wikipedia and have coordinates mentioned in article
    is_important = sparse_column_with_keys(column_name="is_important", keys=["True", "False"]) # defined as OSM names importance of greater than 0.5
    is_most_important_in_timezone = sparse_column_with_keys(column_name="is_most_important_in_timezone", keys=["True", "False"])
    matches_topic = sparse_column_with_keys(column_name="matches_topic", keys=["True", "False"])

    # we don't do a loose index scan, because even that can take a long time when you have tens of millions of records
    time_zones = georefdata.get_timezones()

    matches_end_user_timezone = sparse_column_with_keys(column_name="matches_end_user_timezone", keys=["True", "False", "Unknown"])
    # probably need a cross column here with timezone and user
    median_distance = real_valued_column("median_distance")
    #median_distance_buckets = bucketized_column(median_distance, boundaries=[10,50,100,200,300])
    notability = real_valued_column("notability") #char count of Wikipedia article
    #population = real_valued_column("population")
    #population_buckets = bucketized_column(population, boundaries=[0, 1, 100, 1000, 10000, 100000, 1000000, 10000000, 100000000])
    popularity = real_valued_column("popularity")
    #admin_level_X_median_distance = crossed_column([admin_level, median_distance_buckets], hash_bucket_size=int(1e4))
    #admin_level_X_cluster_frequency = crossed_column([admin_level, cluster_frequency_buckets], hash_bucket_size=int(1e4))
    #admin_level_X_country_code = crossed_column([admin_level, country_code], hash_bucket_size=int(1e4))


    wide_columns = [country_code, country_rank, edit_distance, feature_code, feature_class, importance, is_highest_population, is_important, is_lowest_admin_level, has_mpoly, has_pcode, is_most_important_in_timezone, matches_end_user_timezone, matches_topic, median_distance, popularity]

    crossed_columns = []
    # cross columns
    #pairs = [("favor_local", col.name) for col in wide_columns]
    #pairs = [("favor_local", "matches_end_user_timezone")]
    pairs = [("matches_end_user_timezone", "is_most_important_in_timezone")]
    print "pairs:", pairs
    for name1, name2 in pairs:
        col1 = locals()[name1]
        print "col1:", type(col1)
        col2 = locals()[name2]
        print "col2:", type(col2)
        if hasattr(col1, "lookup_config") and hasattr(col2, "lookup_config"):
            column_name = col1.name + "_X_" + col2.name
            keys = []
            for key1 in col1.lookup_config.keys:
                for key2 in col2.lookup_config.keys:
                    keys.append(key1 + "_X_" + key2)
            new_column = sparse_column_with_keys(column_name=column_name, keys=keys)
            print "new_column:", new_column
            crossed_columns.append(new_column)

    wide_columns += crossed_columns


    """
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
    embedding_column(is_notable, dimension=8),
    importance,
    median_distance_buckets,
    notability,
    population_buckets,
    popularity
]
    """
    deep_columns = []


    include_these_columns_in_local = ['edit_distance', 'feature_class', 'matches_end_user_timezone_X_is_most_important_in_timezone', 'is_most_important_in_timezone']
    exclude_these_columns_in_global = ['matches_end_user_timezone', 'is_most_important_in_timezone', 'matches_end_user_timezone_X_is_most_important_in_timezone']


def get_df_from_features(features):

    try:

        df = get_fake_df()
        add_features_to_df(df, features)
        return df
    except Exception as e:
        print "exception in get_df_from_features:", e

def halve(iterable):
    half = len(iterable) / 2
    return iterable[:half], iterable[half:]

def get_fake_df():
    try:
        return dict([(k, []) for k in COLUMNS])
    except Exception as e:
        print "CAUGHT EXCEPTION IN get_fake_df:", e

def add_features_to_df(df, features):

  try:


    # clean / preprocess
    for feature in features:
        for old_key in feature.keys():
            if old_key.startswith('featureplace__place__'):
                new_key = old_key.replace('featureplace__place__','')
                if len(new_key) > 5: #skip id
                    feature[new_key] = feature[old_key]

    # data frame for training


    if len(features) > 0:
        print "end_user_tz:", features[0]['order__end_user_timezone']

    for index, feature in enumerate(features):

        fid = feature['id']

        end_user_tz = feature['order__end_user_timezone']
        tz = feature['timezone']

        # don't really use feature place id
        #fpid = feature['featureplace__id']

        alternatives = [f for f in features if f['id'] == fid and not feature]
        number_of_alternatives = len(alternatives)
        #print "number_of_alternatives:", number_of_alternatives

        feature_admin_levels = set([f['admin_level'] for f in features if f['admin_level'] and f['id'] == fid])
        if feature_admin_levels:
            lowest_admin_level = min(feature_admin_levels)
        else:
            lowest_admin_level = -99

        if end_user_tz:
            favor_local = True
            matches_end_user_timezone = str(tz == end_user_tz)
        else:
            favor_local = False
            matches_end_user_timezone = "Unknown"


        population = feature['featureplace__place__population']
        is_highest_population = population and population == max([f['population'] for f in features if f['id'] == fid]) or False

        place_id = feature['featureplace__place_id']
        admin_level = feature['admin_level']
        importance = feature["wikipedia__importance"] or 0
        #print "importance:", importance
        is_important = str(importance > 0.75)

        alternatives_in_same_timezone = [alt for alt in alternatives if alt['timezone'] and alt['timezone'] == end_user_tz]
        #print "len(alternatives_in_same_timezone):", len(alternatives_in_same_timezone) 
        alternative_importances = [alt['wikipedia_importance'] for alt in alternatives_in_same_timezone]
        if len(alternative_importances) > 0:
            print "alternative_importances:", alternative_importances
            max_alternative_importance = max(alternative_importances) or 0
            print "max_alternative_importance:", max_alternative_importance
            is_most_important_in_timezone = importance >= max_alternative_importance
        else:
            is_most_important_in_timezone = True

        is_most_important_in_timezone = str(is_most_important_in_timezone)
        #print "is_most_important_in_timezone:", is_most_important_in_timezone
        df['is_most_important_in_timezone'].append(is_most_important_in_timezone)

        notability = feature["featureplace__place__wikipedia__charcount"] or 0
        #df['admin_level'].append(str(admin_level or "None"))
        #df['cluster_frequency'].append(feature['featureplace__cluster_frequency'] or 0)
        df['country_code'].append(feature['featureplace__place__country_code'] or "None")
        df['country_rank'].append(feature['featureplace__country_rank'] or 999)
        df['feature_class'].append(feature['featureplace__place__feature_class'] or "None")
        df['feature_code'].append(feature['featureplace__place__feature_code'] or "None")
        df['has_mpoly'].append(str(feature['featureplace__place__mpoly'] is not None))
        df['has_pcode'].append(str(feature['featureplace__place__pcode'] is not None))
        #df['is_country'].append(str(admin_level == 0))
        df['is_lowest_admin_level'].append(str(lowest_admin_level == admin_level))
        df['is_highest_population'].append(str(is_highest_population))
        df['is_notable'].append(str(bool(notability)))
        df['edit_distance'].append("0")
        df['median_distance'].append(feature['featureplace__median_distance'] or 9999 )
        df['favor_local'].append(str(favor_local))
        df['matches_end_user_timezone'].append(matches_end_user_timezone)
        df['matches_topic'].append(str(feature['topic_id'] == feature["featureplace__place__topic_id"]) if feature['topic_id'] else "False")
        df['notability'].append(notability or 0)
        df['importance'].append(importance or 0)
        df['is_important'].append(is_important)
        #df['population'].append(int(population or 0))
        df['popularity'].append(int(feature['featureplace__popularity'] or 0))
        df['correct'].append(1 if feature['featureplace__correct'] else 0)

        # add crossed column values
        # there should be a more efficient way of doing this 
        for name_of_column in df.keys():
            try:
                if "_X_" in name_of_column:
                    name_of_first_column, name_of_second_column = name_of_column.split("_X_")
                    crossed_value = df[name_of_first_column][-1] + "_X_" + df[name_of_second_column][-1]
                    df[name_of_column].append(crossed_value)
            except Exception as e:
                print "CAUGHT EXCEPTION creating cross column for ", name_of_column, ":", e

  except Exception as e:
    print "CAUGHT EXCEPTION IN add_features_to_df:", e
