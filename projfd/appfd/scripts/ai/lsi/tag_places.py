from appfd.models import Feature, Place, Topic
from appfd.scripts.ai.lsi.get_topic import run as get_topic
from appfd.scripts.ai.lsi.build import run as build
from collections import Counter
from date_extractor import month_to_number
from datetime import datetime

stopwords = [month.lower() for month in list(month_to_number.keys())]

def run(places=None):

    try:

        start = datetime.now()

        if places is None:

            # will probably have to do a yield thing at some point
            #places = Place.objects.exclude(featureplace=None, featureplace__correct=True, featureplace__feature__verified=True)
            places = Place.objects.exclude(featureplace=None)

            place_ids = Feature.objects.filter(featureplace__correct=True, featureplace__feature__verified=True).values_list("featureplace__place_id", flat=True)

        print("place_ids:", len(place_ids))
        for place_id in place_ids:

            counter = Counter()
            for feature in Feature.objects.filter(verified=True, featureplace__place_id=place_id, featureplace__correct=True).exclude(text=None).exclude(text=""):
                if feature.text:
                    topic_id = get_topic(feature.text)
                    if topic_id:
                        counter[topic_id] += 1
                    else:
                        print(feature.text)

            print("counter:", counter)
            most_common_topics = counter.most_common(1)
            if most_common_topics:
                most_common_topic_tuple = most_common_topics[0]
                if most_common_topic_tuple:
                    most_common_topic_id = most_common_topic_tuple[0]
                    print("\tmost_common_topic for", Place.objects.get(id=place_id), "is", Topic.objects.get(id=most_common_topic_id).name)

        print("took", (datetime.now() - start).total_seconds(), "seconds")

    except Exception as e:

        print(e)
        

