from tensorflow import float32
from tensorflow import constant, SparseTensor

CATEGORICAL_COLUMNS = ["admin_level", "country_code", "edit_distance", "feature_class", "feature_code", "has_mpoly", "has_pcode", "is_country", "is_highest_population", "is_lowest_admin_level", "matches_topic"]
CONTINUOUS_COLUMNS = ["cluster_frequency", "country_rank", "median_distance", "population", "popularity"]
LABEL_COLUMN = "correct"
COLUMNS = sorted(CATEGORICAL_COLUMNS + CONTINUOUS_COLUMNS) + [LABEL_COLUMN]

def input_function(d):
  try:

    for column_name in COLUMNS:
        if column_name not in d:
            raise Exception(column_name + " not in d")

    num_rows = len(d['admin_level'])
    feature_cols = {}
    for k in CONTINUOUS_COLUMNS:
        print "k:", k
        feature_cols[k] = constant(d[k], dtype=float32)
    print "CONTINUOUS COLUMNS"

    for k in CATEGORICAL_COLUMNS:
        print "k:", k
        print "y:", len(d[k])
        feature_cols[k] = SparseTensor(
            indices=[[i, 0] for i in range(num_rows)],
            values=d[k],
            shape=[num_rows, 1])
    print "CATEGORICAL COLUMNS:"
    label = constant(d[LABEL_COLUMN])


    return feature_cols, label
  except Exception as e:
    print e
    #fail("EXCEPTION in input_fn: " + str(e))
    #info("Variables are:")
    _locals = locals()
    for k in _locals:
        print k, ":", str(_locals[k])[:25]
