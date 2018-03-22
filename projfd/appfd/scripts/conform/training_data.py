import csv
from collections import defaultdict
from datetime import datetime
from django.db.models.fields.related import ForeignKey
import sys


from appfd import models
from appfd.models import Place


csv.field_size_limit(sys.maxsize)

def get_writer(name):
    f = open("/tmp/" + name.lower(), "w")
    model = getattr(models, name)
    fieldnames = []
    for field in model._meta.fields:
        if isinstance(field, ForeignKey):
            fieldnames.append(field.name + "_id")
        else:
            fieldnames.append(field.name)
    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
    writer.writeheader()
    return writer

order_writer = get_writer("Order")
feature_writer = get_writer("Feature")
featureplace_writer = get_writer("FeaturePlace")


def run():
    try:
        print("starting conform.training_data")
        
        start = datetime.now()
        
        all_titles = set()
        
        # get all titles for links
        with open("/tmp/genesis.tsv") as f:
            for page_id, titles in csv.reader(f, delimiter="\t"):
                for title in titles.split(";"):
                    all_titles.add(title)

        print("first pass took", (datetime.now() - start).total_seconds(), "seconds")

        # convert all titles to list
        all_titles = list(all_titles)
        print("all_titles:", len(all_titles))

        matching_places = list(Place.objects.filter(enwiki_title__in=all_titles))
        print("matching_places:", len(matching_places))

        title2place = dict([(place.enwiki_title, place) for place in matching_places])
        print("title2place")
        
        all_names = list(set([place.name for place in matching_places]))
        print("all_names:", len(all_names))
        print("time:", (datetime.now() - start).total_seconds())
        
        name2placeids = defaultdict(list)
        for i in range(100):
            print("i:", i)
            some_of_the_names = all_names[i: i + 100]
            print("some_of_the_names:", len(some_of_the_names))
            if some_of_the_names:
                print("some of the names are truthy")
                values = list(Place.objects.filter(name__in=some_of_the_names).values_list("name", "id"))
                print("values", type(values))
                if values:
                    print("values are truthy")
                    for name, place_id in values:
                        print(".")
                        name2placeids[name].append(place_id)
            else:
                break
        
        print("gathered all relevant places at ", (datetime.now() - start).total_seconds(), " seconds in")
        
        # second pass for writing data
        with open("/tmp/genesis.tsv") as f:
            line_count = 0
            feature_count = 0
            featureplace_count = 0
            
            for line in csv.reader(f, delimiter="\t"):
                
                line_count += 1
                
                order_id = line_count
                
                page_id, titles = line
                
                # set titles to list
                titles = titles.split(";")

                order_writer.writerow({
                    "id": order_id,
                    "token": page_id
                })
                
                for title in titles:

                    feature_count += 1
                    
                    feature_id = feature_count
                    
                    correct_place = title2place[link]
                    correct_place_id = correct_place.id
                    
                    name = correct_place.name
                    
                    feature_writer.writerow({
                        "id": feature_id,
                        "order_id": order_id,
                        "name": name,
                        "verified": "true"
                    })

                    featureplace_count += 1
                    
                    featureplace_id = featureplace_count

                    # write correct featureplace                        
                    featureplace_writer.writerow({
                        "id": featureplace_id,
                        "feature_id": feature_id,
                        "place_id": place.id,
                        #"cluster_frequency"
                        "confidence": 0.9999,
                        #"country_rank"
                        "correct": "true"
                        #"median_distance"
                        #"sort_order"
                        #"popularity"
                    })
                    
                    # write incorrect feature places
                    for place_id in name2placeids[name]:
                        if place_id != correct_place_id:
                            featureplace_count += 1
                            featureplace_id = featureplace_count
                            featureplace_writer.writerow({
                                "id": featureplace_id,
                                "feature_id": feature_id,
                                "place_id": place_id,
                                "confidence": 0,
                                "correct": "false"
                            })

        print("finishing conform.training_data")
    except Exception as e:
        print(e)

run()

