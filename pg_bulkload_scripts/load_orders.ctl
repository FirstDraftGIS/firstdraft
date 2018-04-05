#
# sample_csv.ctl -- Control file to load CSV input data
#
#    Copyright (c) 2007-2017, NIPPON TELEGRAPH AND TELEPHONE CORPORATION
#
OUTPUT = appfd_order                   # [<schema_name>.]table_name
INPUT = /tmp/order.csv  # Input data location (absolute path)
TYPE = CSV                            # Input file type
QUOTE = "\""                          # Quoting character
ESCAPE = \                            # Escape character for Quoting
DELIMITER = ","                       # Delimiter
