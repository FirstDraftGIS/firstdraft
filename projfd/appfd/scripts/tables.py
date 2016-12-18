from appfd.models import Place
from collections import Counter
# nextRow
# getTables

def doRowsShareTypes(a, b):
    types_a = [type(clean(value)) for value in a]
    types_b = [type(clean(value)) for value in b]


    len_a = len(types_a)
    len_b = len(types_b)
    if abs(len_a - len_b) > 3:
        return False

    min_len = min(len_a, len_b)

    NoneType = type(None)

    for i in range(min_len):
        a_type = types_a[i]
        b_type = types_b[i]
        if a_type != NoneType and b_type != NoneType and a_type != b_type:
            return False

    return True
    
def getHeaderRow(rows):
    print "starting getHeaderRowsFromCSVRows with", rows
    print "\n"
    if rows:
        #if types for the next two rows are the same, but different than the first, we infer that it is a header row
        if doRowsShareTypes(rows[1],rows[2]) and not doRowsShareTypes(rows[0],rows[1]):
            return rows[0]

def clean(value):
    if value == "":
        return None
    try:
        return float(value)
    except:
        return value.strip()

# takes in a sheet and returns which column holds the locations
# erroneously assume that there is only one location column
# rows are lists of lists
def getLocationColumn(rows):

    print "starting getLocationColumn"
    print "with:", rows

    # looks quickly and see if keyword mentioned
    for column_index, value in enumerate(rows[0]):
        if str(value).lower().strip() in ('city','community','country','neighborhood','loc','locations','place','province'):
            print "found location column and returning", column_index
            return column_index

    counter = Counter()
    number_of_rows = len(rows)
    for column_index in range(len(rows[0])):
        values = [rows[row_index][column_index] for row_index in range(1, number_of_rows)]
        counter[column_index] = Place.objects.filter(name__in=values).distinct("name").count()

    print "counter:", counter
    return counter.most_common(1)[0][0]

        #    if not isinstance(value, float) or isinstance(value, int):
        #        if Place.objects.filter(name=value).count() > 0:
        #            return column_index

# takes in a list of lists
# each element in a list of column values
def getLocationsFromColumns(columns):
    return
