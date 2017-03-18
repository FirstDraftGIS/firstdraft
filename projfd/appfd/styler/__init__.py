from appfd.models import Basemap, Feature, FeaturePlace, Order, MapStyle, Place, Style

def style_order(order_id):

    try:

        print "starting style with order_id:", order_id

        basemap_id = Basemap.objects.get(name="OpenStreetMap.Mapnik").id
        map_style_id = MapStyle.objects.create(basemap_id=basemap_id)
        Order.objects.filter(id=order_id).update(style=map_style_id)

        features = Feature.objects.filter(order_id=order_id).values_list("id", flat=True)
        for index, feature_id in enumerate(features):
            label = index < 10 # only display label for first 10, should probably randomize later
            Style.objects.create(feature_id=feature_id, label=label)

    except Exception as e:
        print "[styler.style_order]", e
