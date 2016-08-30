from appfd.models import Order, Feature
from collections import Counter
from tensorflow import constant
from tensorflow.contrib.learn import LinearClassifier
from tensorflow.contrib.layers import sparse_column_with_keys, sparse_column_with_hash_bucket
from tempfile import mkdtemp


#CATEGORICAL_COLUMNS = ["has_pcode","has_mpoly"]
#CONTINUOUS_COLUMNS = ["number_of_other_points_in_country"]


def run():
    try:
        print "starting appbkto.scripts.ai.train"

    #for order_id in Order.objects.values_list("id", flat=True):
    #    print "order_id:", order_id, type(order_id)
    #if True:

        features = Feature.objects.values("correct","place__country_code")
        #print "features:", features
        #country_code_count = Counter([feature['place__country_code'] for feature in features])
        #print "country_code_count:", country_code_count
        #country_name .. will make sure to weight against us because so popular
        #edit_distance = tf.contrib.layers.real_valued_column("edit_distance")
        #has_pcode = sparse_column_with_keys(column_name="has_pcode", keys=[True, False])
        #has_mpoly = sparse_column_with_keys(column_name="has_mpoly", keys=[True, False])
        country_code = sparse_column_with_hash_bucket("country_code", hash_bucket_size=500)
        #number_of_other_points_in_country = sparse_column_with_hash_bucket("number_of_other_points_in_country", hash_bucket_size=1000)
        #number_of_other_points_in_admin1 = sparse_column_with_hash_bucket("number_of_other_points_in_admin1", hash_bucket_size=1000)
        #number_of_other_points_in_admin2 = sparse_column_with_hash_bucket("number_of_other_points_in_admin2", hash_bucket_size=1000)
        #feature_columns = {"country_code": [], "has_pcode":[], "has_mpoly":[]}
        country_codes = []
        labels = []
        number_of_features = len(features)

        with open("/tmp/ai_train.txt", "wb") as f:
            for feature in features[:number_of_features/2]
                country_code = feature['place__country_code'] or ""
                correct = feature['correct'] or ""
                f.write(country_code + "," + correct)

        with open("/tmp/ai_train.txt", "wb") as f:
            for feature in features[number_of_features/2:]
                country_code = feature['place__country_code'] or ""
                correct = feature['correct'] or ""
                f.write(country_code + "," + correct)


        """
        for feature in features:
            #print "feature:", feature
            #feature_columns['country_code'].append(constant((feature.place.country_code))
            #feature_columns['has_pcode'].append(feature.place.pcode is True)
            #feature_columns['has_mpoly'].append(feature.place.mpoly is True)
            #country_codes.append(feature['place__country_code'] or "")
            #labels.append(1 if feature['correct'] else 0)
        print "country_codes:", len(country_codes)
        country_code_tensor = constant(country_codes)
        print "country_code_tensor:", type(country_code_tensor), country_code_tensor
        feature_columns = {}
        feature_columns['country_code'] = country_code_tensor

        labels = constant(labels)

        model_dir = mkdtemp()
        print "model_dir:", model_dir
        #model = tf.contrib.learn.LinearClassifier(feature_columns=[has_pcode, has_mpoly, number_of_other_points_in_country], model_dir=model_dir)
        model = LinearClassifier(feature_columns=[country_code], model_dir=model_dir)
        # train_input_fn returns dict and tensorflow.python.framework.ops.Tensor

        model.fit(input_fn=lambda : (feature_columns, labels), steps=2)

        results = m.evaluate(input_fn=lambda : (feature_columns, labels), steps=1)
        for key in sorted(results):
            print "%s: %s" % (key, results[key])
        """    

    except Exception as e:
        print e
