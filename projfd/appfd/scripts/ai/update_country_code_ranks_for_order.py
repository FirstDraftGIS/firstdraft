from appfd.models import CountryCodeRank, FeaturePlace
from collections import Counter
from datetime import datetime

def run(token):

    try:

        start = datetime.now()


        from django.db import connection
        connection.close()

        print "starting update_country_code_ranks_for_order"

        counter = Counter(FeaturePlace.objects.filter(correct=True, feature__order__token=token).values_list("place__country_code", flat=True)) 

        counts = sorted(list(set(counter.values())), key=lambda v: -1*v)

        CountryCodeRank.objects.filter(order_id=token).delete()

        for country_code, count in counter.items():
            rank = counts.index(count)
            CountryCodeRank.objects.create(country_code=country_code, rank=rank, order_id=token)


    except Exception as e:

        print e
