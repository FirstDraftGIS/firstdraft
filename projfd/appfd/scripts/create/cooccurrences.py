import csv
from collections import defaultdict, Counter
from django.db import connection
from itertools import combinations
from subprocess import check_output
from sys import maxsize

from appfd.models import Cooccurrence
from appfd.utils import get_enwiki_title_to_place_id, save_pickle, load_pickle

def run():
    csv.field_size_limit(maxsize)

    enwiki_title_to_place_id = get_enwiki_title_to_place_id()

    counter = Counter()

    with open("/tmp/genesis.tsv") as f:
        line_count = 0
        for page_id, titles in csv.reader(f, delimiter="\t"):

            line_count += 1

            counter.update(list(combinations(sorted(titles.split(";")), 2)))
            """
            
            titles = titles.split(";")
            
            place_ids = [ enwiki_title_to_place_id[title]
                for title in titles if title in enwiki_title_to_place_id]

            # sort so know which id comes first on lookup
            place_ids.sort()

            counter.update(list(combinations(place_ids, 2)))
            """
            
            if line_count % 1e5 == 0:
                print("pruning counter")
                counter = Counter(dict(counter.most_common(5000000)))
                print("pruned")
                exit()

    numbers = [n for n in check_output("free -m", shell=True).split(b"\n")[1].split(b" ") if n]
    print("size used:", numbers[2])
    print("count:", len(counter))
    save_pickle(counter, "cooccurrences")