import csv
from collections import defaultdict, Counter
from datetime import datetime
from django.db import connection
from django.db.models.fields.related import ForeignKey
import json
import sys


from appfd import models
from appfd.models import Place

start_file = datetime.now()

csv.field_size_limit(sys.maxsize)

# 10 seconds
enwiki_title_to_place_id = dict(Place.objects.exclude(enwiki_title=None).values_list("enwiki_title", "id"))
print("got enwiki_title_to_place_id", (datetime.now() - start_file).total_seconds(), "seconds in")

# 18 seconds
enwiki_title_to_normalized_name = dict(Place.objects.exclude(enwiki_title=None).values_list("enwiki_title", "name_normalized"))
print("got enwiki_title_to_normalized_name", (datetime.now() - start_file).total_seconds(), "seconds in")

# create normalized name to id mapping
# takes about 2 - 6 minutes
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT name_normalized, array_agg(id) AS ids
        FROM appfd_place
        AS subquery
        GROUP BY name_normalized;
    """)
    name2ids = dict(cursor.fetchall())
    print("inserting into took", (datetime.now() - start_file).total_seconds(), "seconds")

# takes about 5 minutes
# popularity is # of times meant place versus number of times didn't
place_id_to_popularity = Counter()
with open("/tmp/genesis.tsv") as f:
    for page_id, titles in csv.reader(f, delimiter="\t"):
        for title in titles.split(";"):
            if title in enwiki_title_to_place_id:
                # add 1 for correct place
                place_id = enwiki_title_to_place_id[title]
                place_id_to_popularity[place_id] += 1
                
                # subtract one for all the other places with the same name
                normalized_name = enwiki_title_to_normalized_name[title]
                for other_place_id in name2ids[normalized_name]:
                    if other_place_id != place_id:
                        place_id_to_popularity[place_id] -= 1
                
print("got popularities", (datetime.now() - start_file).total_seconds(), "seconds in")
print("most common:", place_id_to_popularity.most_common(10))


def get_writer(name):
    f = open("/tmp/" + name.lower() + ".tsv", "w")
    model = getattr(models, name)
    fieldnames = []
    foreign_keys = []
    for field in model._meta.fields:
        if isinstance(field, ForeignKey):
            foreign_keys.append(field.name + "_id")
        else:
            fieldnames.append(field.name)
            
    # add foreign key fields to the end, which is what django does
    fieldnames += foreign_keys
    print("fieldnames:", fieldnames)
    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
    writer.writeheader()
    return writer

order_writer = get_writer("Order")
feature_writer = get_writer("Feature")
featureplace_writer = get_writer("FeaturePlace")

def wrap(items):
    return ["'" + item.replace("'", "''") + "'" for item in items]

def process_group(group, feature_count, featureplace_count):
    
    try:
        
        print("starting process_group")
        
        start_processing_group = datetime.now()
        
        # about 2 seconds
        s = datetime.now()
        enwiki_titles = set()
        for line_count, page_id, titles in group:
            for title in titles:
                enwiki_titles.add(title)
        enwiki_titles = list(enwiki_titles)
        print("grabbing enwiki_titles took", (datetime.now() - s).total_seconds(), "seconds")
        
        # took about 1.5 minutes
        s = datetime.now()
        matching_places = list(Place.objects.filter(enwiki_title__in=enwiki_titles))
        print("grabbing matching_places took", (datetime.now() - s).total_seconds(), "seconds")
       
        # took about half a second
        s = datetime.now()
        title2place = dict([(place.enwiki_title, place) for place in matching_places])
        print("grabbing title2place took", (datetime.now() - s).total_seconds(), "seconds")
        
        # took about half a second
        s = datetime.now()
        normalized_names = list(set([place.name_normalized for place in matching_places]))
        print("grabbing normalized_names took", (datetime.now() - s).total_seconds(), "seconds")

        for line_count, page_id, titles in group:
            
            order_id = line_count
            
            order_writer.writerow({
                "id": order_id,
                "complete": "true",
                "edited": "true",
                "open_source": "true",
                "token": page_id
            })
            
            for title in titles:
                
                if title in title2place:
                    feature_count += 1
                
                    feature_id = feature_count

                    correct_place = title2place[title]
                    correct_place_id = correct_place.id

                    name = correct_place.name
                    name_normalized = correct_place.name_normalized
                        
                    feature_writer.writerow({
                        "geometry_used": "Point",
                        "id": feature_id,
                        "order_id": order_id,
                        "name": name,
                        "verified": "true"
                    })
    
                    featureplace_count += 1
                        
                    featureplace_id = featureplace_count
    
                    featureplace_writer.writerow({
                        "id": featureplace_id,
                        "feature_id": feature_id,
                        "place_id": correct_place_id,
                        "confidence": 0.9999,
                        "correct": "true",
                        "popularity": place_id_to_popularity[correct_place_id]
                    })
                        
                    # write incorrect feature places
                    for place_id in name2ids[name_normalized]:
                        if place_id != correct_place_id:
                            featureplace_count += 1
                            featureplace_id = featureplace_count
                            featureplace_writer.writerow({
                                "id": featureplace_id,
                                "feature_id": feature_id,
                                "place_id": place_id,
                                "confidence": 0,
                                "correct": "false",
                                "popularity": place_id_to_popularity[place_id]
                            })

        print("process_group took", (datetime.now() - start_processing_group).total_seconds(), "seconds")

        return feature_count, featureplace_count
        
    except Exception as e:
        print("caught exception processing group:", e)
        raise(e)

def run():
    try:
        print("starting conform.training_data")
        
        start = datetime.now()
        
        line_count = 0
        feature_count = 0
        featureplace_count = 0
        group = []

        # get all titles for links
        with open("/tmp/genesis.tsv") as f:
            for page_id, titles in csv.reader(f, delimiter="\t"):
                line_count += 1
                group.append((line_count, page_id, titles.split(";")))
                
                if line_count % 500000 == 0:
                    feature_count, featureplace_count = process_group(group, feature_count, featureplace_count)
                    group = []

        process_group(group, feature_count, featureplace_count)
        
        print("conform.training_data took", (datetime.now() - start).total_seconds(), "seconds")
        print("finishing conform.training_data")
    except Exception as e:
        print(e)
        raise(e)
