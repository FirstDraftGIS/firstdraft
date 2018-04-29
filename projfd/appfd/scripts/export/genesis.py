import csv
from collections import defaultdict, Counter
from datetime import datetime
from django.db import connection
from django.db.models.fields.related import ForeignKey
import json
import pickle
from os.path import isfile
from pandas import read_csv
from projfd.settings import FILEPATH_OF_MARGE_TRAINING_DATA
import sys

from appfd.utils import get_enwiki_title_to_place_id, get_sorted_field_names, load_pickle, save_pickle
from appfd.models import Place

start_file = datetime.now()

csv.field_size_limit(sys.maxsize)


enwiki_title_to_place_id = get_enwiki_title_to_place_id()

enwiki_title_to_normalized_name = load_pickle("enwiki_title_to_normalized_name")
if enwiki_title_to_normalized_name is None:
    enwiki_title_to_normalized_name = dict(Place.objects.exclude(enwiki_title=None).values_list("enwiki_title", "name_normalized"))
    save_pickle(enwiki_title_to_normalized_name, "enwiki_title_to_normalized_name")
print("got enwiki_title_to_normalized_name", (datetime.now() - start_file).total_seconds(), "seconds in")
 
name2ids = load_pickle("name2ids")
if name2ids is None:
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name_normalized, array_agg(id) AS ids
            FROM appfd_place
            AS subquery
            GROUP BY name_normalized;
        """)
        name2ids = dict(cursor.fetchall())
    save_pickle(name2ids, "name2ids")
print("inserting into took", (datetime.now() - start_file).total_seconds(), "seconds")
    

place_id_to_popularity = load_pickle("place_id_to_popularity")
if place_id_to_popularity is None:
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
    save_pickle(place_id_to_popularity, "place_id_to_popularity")
    
print("got popularities", (datetime.now() - start_file).total_seconds(), "seconds in")
print("most common:", place_id_to_popularity.most_common(10))
for place_id, count in place_id_to_popularity.most_common(10):
    print(Place.objects.get(id=place_id).name_normalized)

exclude_these = ["mls", "mpoly", "name", "name_ascii", "name_en", "name_display", "other_names", "skeleton"]
place_sorted_fieldnames = get_sorted_field_names(Place)
include_these = [fieldname for fieldname in place_sorted_fieldnames if fieldname not in exclude_these]
print("include_these:", include_these)

def get_fieldnames():
    fieldnames = [
        "id",
        "feature_id",
        "order_id",
        "feature_name",
        "correct",
        "popularity"
    ]
    
    for field_name in place_sorted_fieldnames:
        if field_name in exclude_these:
            print("skipping over fields not used for ML training")
        elif field_name == "id":
            fieldnames.append("place_id")
        else:
            fieldnames.append(field_name)
    
    print("fn:", fieldnames)
    
    return fieldnames


f = open("/tmp/firstdraftgis_export.tsv", "w")
fieldnames = get_fieldnames()
writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
writer.writeheader()

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
        
        # get normalized names
        s = datetime.now()
        normalized_names = list(Place.objects.exclude(enwiki_title=None).filter(enwiki_title__in=enwiki_titles).values_list("name_normalized", flat=True).distinct())
        print("grabbing normalized_names took", (datetime.now() - s).total_seconds(), "seconds")
        
        # get all places that match normalized names
        s = datetime.now()
        places = Place.objects.filter(name_normalized__in=normalized_names).values(*include_these)
        print("grabbing places took", (datetime.now() - s).total_seconds(), "seconds")
        
        s = datetime.now()
        id2place = dict([(place["id"], place) for place in places])
        print("generating id2place took", (datetime.now() - s).total_seconds(), "seconds")
        
        s = datetime.now()
        matching_places = [place for place in places if place["enwiki_title"] in enwiki_titles]
        print("grabbing matching_places took", (datetime.now() - s).total_seconds(), "seconds")
       
        # took about half a second
        s = datetime.now()
        title2place = dict([(place["enwiki_title"], place) for place in matching_places])
        print("grabbing title2place took", (datetime.now() - s).total_seconds(), "seconds")

        for line_count, page_id, titles in group:
            
            order_id = line_count
            
            for title in titles:
                
                if title in title2place:
                    feature_count += 1
                
                    feature_id = feature_count

                    correct_place = title2place[title]
                    correct_place_id = correct_place["id"]

                    name_normalized = correct_place["name_normalized"]
    
                    featureplace_count += 1
                        
                    featureplace_id = featureplace_count
    
                    newdict = {
                        "id": featureplace_id,
                        "feature_id": feature_id,
                        "place_id": correct_place_id,
                        "correct": "true",
                        "popularity": place_id_to_popularity[correct_place_id],
                        "order_id": order_id
                    }
                    writer.writerow({**newdict, **correct_place})
                        
                    # write incorrect feature places
                    for place_id in name2ids[name_normalized]:
                        if place_id != correct_place_id:
                            incorrect_place = id2place[place_id]
                            featureplace_count += 1
                            featureplace_id = featureplace_count
                            newdict = {
                                "id": featureplace_id,
                                "feature_id": feature_id,
                                "place_id": place_id,
                                "correct": "false",
                                "popularity": place_id_to_popularity[place_id],
                                "order_id": order_id
                            }
                            writer.writerow({**newdict, **incorrect_place})

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
                
                if line_count % 5000 == 0:
                    print("line_count:", line_count)
                    feature_count, featureplace_count = process_group(group, feature_count, featureplace_count)
                    group = []

        process_group(group, feature_count, featureplace_count)
        
        print("conform.training_data took", (datetime.now() - start).total_seconds(), "seconds")
        print("finishing conform.training_data")
    except Exception as e:
        print(e)
        raise(e)
