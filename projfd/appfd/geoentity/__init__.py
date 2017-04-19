from django.contrib.gis.geos import GEOSGeometry

trues = ("T", "t", "True", "true", True, "Yes", "y", "yes")

class GeoEntity(object):

    def __init__(self, row):
        try:
            print "row:", row
            print "len(row):", len(row)
            self.place_id = row[0]
            self.admin_level = str(row[1])
            self.country_code = row[2]
            self.admin1code = row[3] or None
            self.country_rank = row[4] or 999
            self.target, self.edit_distance = row[5].split("--")
            self.edit_distance = int(self.edit_distance)
            self.place_name = row[6]
            self.alias = row[7]
            self.population = int(row[8] or 0)
            self.point = GEOSGeometry(row[9])
            topic_id = row[10]
            self.topic_id = int(topic_id) if topic_id else None
            self.has_mpoly = row[11] in trues
            print "row[11]:", row[11] in trues
            self.has_pcode = row[12] in trues

            # popularity will be None if not used yet
            self.popularity = 0 if row[13] is None else int(row[13])

            self.feature_class = row[14]
            self.feature_code = row[15]
            self.notability = int(row[16] or 0)
        except Exception as e:
            print "EXCEPTION in GeoEntity.__init__:", e
            raise e
