try:
    from appfd.models import Order, Place, Topic
    from controlcenter import Dashboard, widgets
    from django.db.models import Count 

    class LeastPopularPlaces(widgets.SingleBarChart):
        values_list = ('name', 'popularity')
        queryset = Place.objects.exclude(popularity=None).order_by('popularity')[:10]
        limit_to = 10
        width = widgets.LARGEST

    class MostPopularPlaces(widgets.SingleBarChart):
        values_list = ('name', 'popularity')
        queryset = Place.objects.exclude(popularity=None).order_by('-popularity')[:10]
        limit_to = 10
        width = widgets.LARGEST

    class MostNotablePlaces(widgets.SingleBarChart):
        values_list = ("name", "wikipedia__charcount")
        queryset = Place.objects.exclude(wikipedia__charcount=None).order_by("-wikipedia__charcount")[:10]
        limit_to = 10
        width = widgets.LARGEST

    class NumberOfOrdersPerDayInLast7Days(widgets.SingleLineChart):
        title = "Number of Orders (Last 7 Days)"
        limit_to = 7
        queryset = Order.objects.extra({'day': "date_trunc('day', start)"}).extra({'epoch': "cast(extract(epoch from date_trunc('day', start)) as integer)"}).values('day', 'epoch').annotate(Count('id')).order_by("-epoch")[:7]
        width = widgets.LARGEST

        def labels(self):
            print "STARTING LABELS"
            return [d['day'].strftime("%m-%d") for d in self.queryset]

        def series(self):
            print "SERIES"
            return [list(self.queryset.values_list("id__count", flat=True))]

    class NumberOfOrdersPerDayInLast30Days(widgets.SingleLineChart):
        title = "Number of Orders (Last 30 Days)"
        values_list = ["epoch", "id__count"]
        queryset = Order.objects.extra({'day': "date_trunc('day', start)"}).extra({'epoch': "cast(extract(epoch from date_trunc('day', start)) as integer)"}).values('day', 'epoch').annotate(Count('id')).order_by("-epoch")[:30]
        width = widgets.LARGEST

    class Topics(widgets.ItemList):
        model = Topic
        values_list = ("name")

    class MyDashboard(Dashboard):
        widgets = [
            NumberOfOrdersPerDayInLast7Days,
            NumberOfOrdersPerDayInLast30Days,
            MostPopularPlaces,
            LeastPopularPlaces,
            MostNotablePlaces,
            Topics
        ]

except Exception as e:

    print "CAUGHT ERROR IN dashboards.py:", e
