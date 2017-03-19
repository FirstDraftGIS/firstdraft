from appfd.models import Basemap, Feature, FeaturePlace, Order, MapStyle, Place, Style

def style_order(order_id, style=None):

    try:

        print "starting style with order_id:", order_id, style

        #basemap_name = style['basemap'] if style and "basemap" in style else "OpenStreetMap.Mapnik"
        #basemap_id = Basemap.objects.get(name=basemap_name).id
        if style and "basemap" in style:
            map_style_id = MapStyle.objects.create(basemap=style['basemap'])
        else:
            map_style_id = MapStyle.objects.create()

        Order.objects.filter(id=order_id).update(style=map_style_id)

        features = Feature.objects.filter(order_id=order_id).values_list("id", flat=True)
        for index, feature_id in enumerate(features):
            label = index < 10 # only display label for first 10, should probably randomize later
            Style.objects.create(feature_id=feature_id, label=label)

    except Exception as e:
        print "[styler.style_order]", e
