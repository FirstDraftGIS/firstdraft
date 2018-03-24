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


# create mapping used later
cursor = connection.cursor()
cursor.execute("DROP TABLE IF EXISTS name_normalized_2_place_ids;")
cursor.execute("""
SELECT name_normalized, array_agg(id) AS ids
INTO name2ids
FROM appfd_place
AS subquery
GROUP BY name_normalized;
""")
print("inserting into took", (datetime.now() - start_file).total_seconds(), "seconds")
start_indexing = datetime.now()
cursor.execute("CREATE UNIQUE INDEX name2ids_idx ON name2ids (name_normalized);")
print("indexing took", (datetime.now() - start_indexing).total_seconds(), "seconds")


def get_writer(name):
    f = open("/tmp/" + name.lower() + ".tsv", "w")
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

def wrap(items):
    return ["'" + item.replace("'", "''") + "'" for item in items]

def process_group(group, feature_count, featureplace_count):
    
    try:
        
        print("starting process_group")
        
        start_processing_group = datetime.now()
        
        s = datetime.now()
        enwiki_titles = set()
        for line_count, page_id, titles in group:
            for title in titles:
                enwiki_titles.add(title)
        enwiki_titles = list(enwiki_titles)
        print("grabbing enwiki_titles took", (datetime.now() - s).total_seconds(), "seconds")
        
        s = datetime.now()
        matching_places = list(Place.objects.filter(enwiki_title__in=enwiki_titles))
        print("grabbing matching_places took", (datetime.now() - s).total_seconds(), "seconds")
       
        s = datetime.now()
        title2place = dict([(place.enwiki_title, place) for place in matching_places])
        print("grabbing title2place took", (datetime.now() - s).total_seconds(), "seconds")
        
        s = datetime.now()
        normalized_names = list(set([place.name_normalized for place in matching_places]))
        print("grabbing normalized_names took", (datetime.now() - s).total_seconds(), "seconds")
        
        s = datetime.now()
        normalized_name_2_place_ids = defaultdict(list)
        cursor = connection.cursor()
        statement = """
            SELECT name_normalized, ids
            FROM name2ids
            WHERE name_normalized=ANY(ARRAY[""" + ",".join(wrap(normalized_names)) + """]);
        """
        #print(statement)
        cursor.execute(statement)
        normalized_name_2_place_ids = dict(cursor.fetchall())
        #print("normalized_name_2_place_ids:", str(normalized_name_2_place_ids))
        print("grabbing normalized_name_2_place_ids took", (datetime.now() - s).total_seconds(), "seconds")
        
        for line_count, page_id, titles in group:
            
            order_id = line_count
            
            order_writer.writerow({
                "id": order_id,
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
                        "place_id": correct_place.id,
                        "confidence": 0.9999,
                        "correct": "true"
                    })
                        
                    # write incorrect feature places
                    for place_id in normalized_name_2_place_ids[name_normalized]:
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
