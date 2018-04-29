from datetime import datetime
from django.db.models.fields.related import ForeignKey
from os.path import isfile
import pickle

from appfd.models import Place

def get_sorted_field_names(model):
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
    
    return fieldnames
    
def load_pickle(filename):
    filepath = "/tmp/" + filename + ".pickle"
    if isfile(filepath):
        with open(filepath, "rb") as f:
            return pickle.load(f)
    else:
        print("couldn't load " + filepath + " because it doesn't exist")

def save_pickle(obj, filename):
    filepath = "/tmp/" + filename + ".pickle"
    with open(filepath, "wb") as f:
        pickle.dump(obj, f)
    print("saved " + filename + " to " + filepath)

def get_enwiki_title_to_place_id():
    enwiki_title_to_place_id = load_pickle("enwiki_title_to_place_id")
    if enwiki_title_to_place_id is None:
        enwiki_title_to_place_id = dict(Place.objects.exclude(enwiki_title=None).values_list("enwiki_title", "id"))
        save_pickle(enwiki_title_to_place_id, "enwiki_title_to_place_id")
    return enwiki_title_to_place_id