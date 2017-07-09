from appfd.models import Place
from django.db import connection
from tensorflow.contrib.layers import bucketized_column, crossed_column, embedding_column, sparse_column_with_keys, sparse_column_with_hash_bucket, real_valued_column

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


CATEGORICAL_COLUMNS = ["country_code", "edit_distance", "feature_class", "feature_code", "has_mpoly", "has_pcode", "is_highest_population", "is_lowest_admin_level", "matches_end_user_timezone", "matches_topic", "is_notable"]
CONTINUOUS_COLUMNS = ["country_rank", "median_distance", "notability", "popularity", "importance"]
LABEL_COLUMN = "correct"
COLUMNS = sorted(CATEGORICAL_COLUMNS + CONTINUOUS_COLUMNS) + [LABEL_COLUMN]


#number_of_other_points_in_country = sparse_column_with_hash_bucket("number_of_other_points_in_country", hash_bucket_size=1000)
#number_of_other_points_in_admin1 = sparse_column_with_hash_bucket("number_of_other_points_in_admin1", hash_bucket_size=1000)
#number_of_other_points_in_admin2 = sparse_column_with_hash_bucket("number_of_other_points_in_admin2", hash_bucket_size=1000)

#admin_level = sparse_column_with_keys(column_name="admin_level", keys=["None","0","1","2","3","4","5","6"]) # I've never seen admin 6, but you never know!
#cluster_frequency = real_valued_column("cluster_frequency")
#cluster_frequency_buckets = bucketized_column(cluster_frequency, boundaries=[0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1])

cursor.execute(loose_index_scan.format("country_code"))
country_codes = sorted(list(set([_tup[0].upper() for _tup in cursor.fetchall() if _tup[0]])))
country_code = sparse_column_with_keys("country_code", keys=country_codes)

country_rank = real_valued_column("country_rank")
edit_distance = sparse_column_with_keys(column_name="edit_distance", keys=["0", "1", "2"])

#feature_classes = list(Place.objects.values_list("feature_class", flat=True).distinct())
cursor.execute(loose_index_scan.format("feature_class"))
feature_classes = sorted(list(set([_tup[0].upper() for _tup in cursor.fetchall() if _tup[0]])))
feature_class = sparse_column_with_keys("feature_class", keys=feature_classes)

#feature_codes = list(Place.objects.values_list("feature_code", flat=True).distinct())
cursor.execute(loose_index_scan.format("feature_code"))
feature_codes = sorted(list(set([_tup[0].upper() for _tup in cursor.fetchall() if _tup[0]])))
feature_code = sparse_column_with_keys("feature_code", keys=feature_codes)

has_pcode = sparse_column_with_keys(column_name="has_pcode", keys=["True", "False"])
has_mpoly = sparse_column_with_keys(column_name="has_mpoly", keys=["True", "False"])
importance = real_valued_column("importance")
#is_country = sparse_column_with_keys(column_name="is_country", keys=["True", "False"])
is_lowest_admin_level = sparse_column_with_keys(column_name="is_lowest_admin_level", keys=["True", "False"])
is_highest_population = sparse_column_with_keys(column_name="is_highest_population", keys=["True", "False"])
is_notable = sparse_column_with_keys(column_name="is_notable", keys=["True", "False"]) # does it appear in Wikipedia and have coordinates mentioned in article
matches_topic = sparse_column_with_keys(column_name="matches_topic", keys=["True", "False"])
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


wide_columns = [country_code, country_rank, edit_distance, feature_code, feature_class, importance, is_highest_population, is_lowest_admin_level, has_mpoly, has_pcode, matches_topic, median_distance, popularity]
#wide_columns = [is_lowest_admin_level]
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

    # data frame for training
    for index, feature in enumerate(features):

        fid = feature['id']
        fpid = feature['featureplace__id']

        feature_admin_levels = set([f['featureplace__place__admin_level'] for f in features if f['featureplace__place__admin_level'] and f['id'] == fid])
        if feature_admin_levels:
            lowest_admin_level = min(feature_admin_levels)
        else:
            lowest_admin_level = -99

        if feature['order__end_user_timezone']:
            matches_end_user_timezone = str(feature['featureplace__place__timezone'] == feature['order__end_user_timezone'])
        else:
            matches_end_user_timezone = "Unknown"


        population = feature['featureplace__place__population']
        is_highest_population = population and population == max([f['featureplace__place__population'] for f in features if f['id'] == fid]) or False

        place_id = feature['featureplace__place_id']
        admin_level = feature['featureplace__place__admin_level']
        importance = feature["featureplace__place__wikipedia__importance"] or 0
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
        df['matches_end_user_timezone'].append(matches_end_user_timezone)
        df['matches_topic'].append(str(feature['topic_id'] == feature["featureplace__place__topic_id"]) if feature['topic_id'] else "False")
        df['notability'].append(notability or 0)
        df['importance'].append(importance or 0)
        #df['population'].append(int(population or 0))
        df['popularity'].append(int(feature['featureplace__popularity'] or 0))
        df['correct'].append(1 if feature['featureplace__correct'] else 0)

  except Exception as e:
    print "CAUGHT EXCEPTION IN add_features_to_df:", e
