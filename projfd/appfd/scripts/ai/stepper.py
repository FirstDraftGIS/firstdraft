#import inspect
from datetime import datetime
from tensorflow import float32
from tensorflow import constant, SparseTensor

def step(d):

    try:

        """
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        print 'function name "%s"' % inspect.getframeinfo(frame)[2]
        for i in args:
            print "    %s = %s" % (i, values[i])
        """

        start = datetime.now()

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
        print "label:", label

        print "step took:", (datetime.now() - start).total_seconds(), "seconds"

        return (feature_cols, label)
    except Exception as e:
        print "EXCEPTION in input_fn: " + str(e)
        print "Variables are:"
        _locals = locals()
        for k in _locals:
            print k, ":", str(_locals[k])[:25]
