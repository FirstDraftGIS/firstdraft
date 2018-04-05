# basically, we're exporting so MARGE can consume it
import csv
from appfd.models import Place
from appfd.utils import get_sorted_field_names
from pandas import read_csv
from projfd.settings import FILEPATH_OF_MARGE_TRAINING_DATA


exclude_these = ["mls", "mpoly", "name", "name_ascii", "name_en", "name_display", "other_names", "skeleton"]
place_sorted_fieldnames = get_sorted_field_names(Place)
place_value_keys = [fieldname for fieldname in place_sorted_fieldnames if fieldname not in exclude_these]
print("place_value_keys:", place_value_keys)

def get_fieldnames():
    fieldnames = [
        "order_id",
        "feature_id",
        "featureplace_id",
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

def run():
    print("starting export of conformed genesis training data")
    
    output_file = open(FILEPATH_OF_MARGE_TRAINING_DATA, "w")
    writer = csv.DictWriter(output_file, fieldnames=get_fieldnames())
    writer.writeheader()

    for chunk in read_csv("/tmp/featureplace.tsv", chunksize=1e5, sep="\t"):
        places = Place.objects.filter(id__in=chunk["place_id"].tolist()).values(*place_value_keys)
        id2place = dict([(place["id"], place) for place in places])
        for index, row in chunk.iterrows():
            combined = {**row, **id2place[row["place_id"]]}
            combined["place_id"] = combined.pop("id")
            for key in ['median_distance', 'country_rank', 'cluster_frequency', 'sort_order', 'confidence']:
                del combined[key]
            writer.writerow(combined)

    output_file.close()
    print("finished exporting genesis data")