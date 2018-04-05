import csv

from appfd.models import Feature, Order, Place, Source

from appfd.utils import get_sorted_field_names

# export that marge uses to train data
def run():
    
    try:
        
        field_names = [
            "order_id",
            "feature_id",
            "featureplace_id",
            "feature_name",
            "correct",
            "popularity",
            "place_id"
        ]
        
        for field_name in get_sorted_field_names(Place):
            if field_name != "id":
                field_names.append(field_name)
                
        print("field_names:", field_names)

        with open("exported_data.tsv", "w") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
        
        """
        Doing this in pieces, by order then feature, in order to minimize
        impact on memory, prioritizing reliability over speed
        """
        for order in Order.objects.all():
            order_id = order.id
            for feature in order.feature_set.all():
                feature_id = feature.id
                feature_name = feature.name
                for featureplace in feature.featureplace_set.all():
                    featureplace_id = featureplace.id
                    row = {
                        "order_id": order_id,
                        "feature_id": feature_id,
                        "featureplace_id": featureplace_id,
                        "feature_name": feature_name,
                        "correct": featureplace.correct,
                        "popularity_at_decision_time": featureplace.popularity
                    }
                    for key, value in featureplace.place.values().items():
                        if key in field_names:
                            row[key] = value

                    with open("exported_data.tsv", "a") as f:
                        csv.DictWriter(f, fieldnames=fieldnames).writerow(row)

        
    except Exception as e:
        print(e)