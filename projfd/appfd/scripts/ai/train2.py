from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tempfile
import urllib

import pandas as pd
import tensorflow as tf

flags = tf.app.flags
FLAGS = flags.FLAGS

flags.DEFINE_string("model_dir", "", "Base directory for output models.")
flags.DEFINE_string("model_type", "wide_n_deep", "Valid model types: {'wide', 'deep', 'wide_n_deep'}.")
flags.DEFINE_integer("train_steps", 20, "Number of training steps.")
flags.DEFINE_string("train_data", "", "Path to the training data.")
flags.DEFINE_string(
    "test_data",
    "",
    "Path to the test data.")

#COLUMNS = ["age", "workclass", "fnlwgt", "education", "education_num",
#           "marital_status", "occupation", "relationship", "race", "gender",
#           "capital_gain", "capital_loss", "hours_per_week", "native_country",
#           "income_bracket"]
COLUMNS = ["country_code","country_code_count","score"]
LABEL_COLUMN = "label"
#CATEGORICAL_COLUMNS = ["workclass", "education", "marital_status", "occupation",
#                       "relationship", "race", "gender", "native_country"]
#CONTINUOUS_COLUMNS = ["age", "education_num", "capital_gain", "capital_loss",
#                      "hours_per_week"]
CONTINUOUS_COLUMNS = ["country_code_count"]
CATEGORICAL_COLUMNS = ["country_code"]

def build_estimator(model_dir):
  country_code = tf.contrib.layers.sparse_column_with_hash_bucket("country_code", hash_bucket_size=400)
  country_code_count = tf.contrib.layers.real_valued_column("country_code_count")
  feature_columns = [country_code, country_code_count]
  return tf.contrib.learn.LinearClassifier(model_dir=model_dir, feature_columns=feature_columns)


def input_fn(df):
  """Input builder function."""
  # Creates a dictionary mapping from each continuous feature column name (k) to
  # the values of that column stored in a constant Tensor.
  continuous_cols = {k: tf.constant(df[k].values) for k in CONTINUOUS_COLUMNS}
  # Creates a dictionary mapping from each categorical feature column name (k)
  # to the values of that column stored in a tf.SparseTensor.
  print("x:", CONTINUOUS_COLUMNS)
  categorical_cols = {k: tf.SparseTensor(
      indices=[[i, 0] for i in range(df[k].size)],
      values=df[k].values,
      shape=[df[k].size, 1])
                      for k in CATEGORICAL_COLUMNS}
  # Merges the two dictionaries into one.
  feature_cols = dict(continuous_cols)
  feature_cols.update(categorical_cols)
  # Converts the label column into a constant Tensor.
  label = tf.constant(df[LABEL_COLUMN].values)
  # Returns the feature columns and the label.
  return feature_cols, label


def train_and_eval():
  """Train and evaluate the model."""
  #train_file_name, test_file_name = maybe_download()
  train_file_name = "/tmp/ai_train.csv"
  test_file_name = "/tmp/ai_test.csv"
  df_train = pd.read_csv(
      tf.gfile.Open(train_file_name),
      names=COLUMNS,
      skipinitialspace=True)
  df_test = pd.read_csv(
      tf.gfile.Open(test_file_name),
      names=COLUMNS,
      skipinitialspace=True,
      skiprows=1)

  df_train[LABEL_COLUMN] = (df_train["score"].apply(lambda x: "correct" in x)).astype(int)
  df_test[LABEL_COLUMN] = (df_test["score"].apply(lambda x: "correct" in x)).astype(int)

  model_dir = tempfile.mkdtemp() if not FLAGS.model_dir else FLAGS.model_dir
  print("model directory = %s" % model_dir)

  m = build_estimator(model_dir)
  m.fit(input_fn=lambda: input_fn(df_train), steps=FLAGS.train_steps)
  results = m.evaluate(input_fn=lambda: input_fn(df_test), steps=1)
  for key in sorted(results):
    print("%s: %s" % (key, results[key]))


def main(_):
  train_and_eval()


if __name__ == "__main__":
  tf.app.run()
