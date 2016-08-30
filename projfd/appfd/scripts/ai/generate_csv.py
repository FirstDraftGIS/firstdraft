from appfd.models import Order, Feature
from collections import Counter
from csv import QUOTE_MINIMAL, writer

def split_list(a_list):
    half = len(a_list)/2
    return a_list[:half], a_list[half:]

def run():
  try:
    print "starting appbkto.scripts.ai.generate_csv"

    order_ids_for_training, order_ids_for_testing = split_list(Order.objects.values_list("id", flat=True))

    with open("/tmp/ai_train.csv", "wb") as f:
        w = writer(f, delimiter=',', quotechar='"', quoting=QUOTE_MINIMAL)
        for order_id in order_ids_for_training:
            features = Feature.objects.filter(order_id=order_id).values("correct","place__country_code")
            country_code_counter = Counter([feature['place__country_code'] for feature in features])
            print "country_code_counter", country_code_counter
            for index, feature in enumerate(features):
                country_code = feature['place__country_code'] or "NONE"
                country_code_count = str(country_code_counter[country_code]) if country_code else "0"
                correct = "correct" if feature['correct'] else "wrong"
                w.writerow([country_code,country_code_count,correct])

    with open("/tmp/ai_test.csv", "wb") as f:
        w = writer(f, delimiter=',', quotechar='"', quoting=QUOTE_MINIMAL)
        for order_id in order_ids_for_testing:
            features = Feature.objects.filter(order_id=order_id).values("correct","place__country_code")
            country_code_counter = Counter([feature['place__country_code'] for feature in features])
            print "country_code_counter", country_code_counter
            for index, feature in enumerate(features):
                country_code = feature['place__country_code'] or "NONE"
                country_code_count = str(country_code_counter[country_code]) if country_code else "0"
                correct = "correct" if feature['correct'] else "wrong"
                w.writerow([country_code,country_code_count,correct])


    print "finished appbkto.scripts.ai.generate_csv"
  except Exception as e:
    print e
