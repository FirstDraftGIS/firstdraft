from tensorflow.contrib.layers import bucketized_column, crossed_column, embedding_column, sparse_column_with_keys, sparse_column_with_hash_bucket, real_valued_column

CATEGORICAL_COLUMNS = ["admin_level", "country_code", "edit_distance", "feature_class", "feature_code", "has_mpoly", "has_pcode", "is_country", "is_highest_population", "is_lowest_admin_level", "matches_topic"]
CONTINUOUS_COLUMNS = ["cluster_frequency", "country_rank", "median_distance", "population", "popularity"]
LABEL_COLUMN = "correct"
COLUMNS = sorted(CATEGORICAL_COLUMNS + CONTINUOUS_COLUMNS) + [LABEL_COLUMN]


#number_of_other_points_in_country = sparse_column_with_hash_bucket("number_of_other_points_in_country", hash_bucket_size=1000)
#number_of_other_points_in_admin1 = sparse_column_with_hash_bucket("number_of_other_points_in_admin1", hash_bucket_size=1000)
#number_of_other_points_in_admin2 = sparse_column_with_hash_bucket("number_of_other_points_in_admin2", hash_bucket_size=1000)

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

def get_df_from_features(features):

    df = get_fake_df()
    add_features_to_df(df, features)
    return df

def halve(iterable):
    half = len(iterable) / 2
    return iterable[:half], iterable[half:]

def get_fake_df():
    return dict([(k, []) for k in COLUMNS])

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
