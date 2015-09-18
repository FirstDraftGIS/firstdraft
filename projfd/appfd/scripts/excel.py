from appfd.models import Place
# should add to openpyxl
# nextRow
# getTables

def doRowsShareTypes(a, b):
    types_a = [type(cell.value) for cell in a]
    types_b = [type(cell.value) for cell in b]


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
    
# returns none if no header row
def getHeaderRow(row, rows=None):
    types = []
    values = []
    for cell in row:
        #print "cell is", dir(cell)
        #print "cell.value", cell.value
        #print "a is ", type(cell.value)
        value = cell.value
        values.append(value)

        # try the easy way and see if a cell in the row is a term most often found in a header
        #if isinstance(value,unicode) and value.lower() in ("lat","lon","latitude","longitude","place","location","address"):
        #    return True

        # else, check if the header is of different content_type than the rows of the table 
        types.append(type(cell.value))
    #print "types are", types

    
    if rows:
        #if types for the next two rows are the same, but different than the first, we infer that it is a header row
        if doRowsShareTypes(rows[1],rows[2]) and not doRowsShareTypes(rows[0],rows[1]):
            return values

def cleanCellValue(value):
    if isinstance(value,float) or isinstance(value,int):
        return value
    elif isinstance(value, str) or isinstance(value, unicode):
        return value.strip().strip('"').strip('"').strip()

# takes in a sheet and returns which column holds the locations
# erroneously assume that there is only one location column
def getLocationColumn(sheet):
    # looks quickly and see if keyword mentioned
    columns = sheet.columns
    for index, column in enumerate(columns):
        if str(column[0].value).lower().strip() in ('city','community','country','neighborhood','loc','locations','place','province'):
            return index

    for index, column in enumerate(columns):
        value = column[1].value

        # assuming that place names can't be numbers
        if not isinstance(value, float) or isinstance(value, int):
            if Place.objects.filter(name=value).count() > 0 or Place.objects.filter(name=column[2].value).count() > 0:
                return index
