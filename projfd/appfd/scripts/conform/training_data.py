import csv

from appfd.models import Order, Place


order_file = open("/tmp/orders.tsv", "w")
order_field_names = [field.name for field in Order._meta.fields]
order_DictWriter = csv.DictWriter(order_file, fieldnames=order_field_names, delimiter="\t")
order_DictWriter.writeheader()

def run():
    try:
        print("starting conform.training_data")
        with open("/tmp/genesis.tsv") as f:
            count = 0
            group_lines = []
            group_titles = set()
            for line in csv.reader(f, delimiter="\t"):
                count += 1
                page_id, titles = line
                
                # set titles to list
                titles = titles.split(";")
                
                # store set of all titles for query db later
                for title in titles:
                    group_titles.add(title)
                
                group_lines.append((count, page_id, titles))
                
                if count % 10 == 0:
    
                    title2place = dict([
                        (place.enwiki_title, place) for place in Place.objects.filter(enwiki_title__in=list(group_titles))
                    ])
                    
                    for count, page_id, links in group_lines:
                        order_DictWriter.writerow({
                            "id": count,
                            "token": page_id
                        })
                    
                    
                    group_lines = []
                    group_titles = set()
                    break
        print("finishing conform.training_data")
    except Exception as e:
        print(e)

run()

