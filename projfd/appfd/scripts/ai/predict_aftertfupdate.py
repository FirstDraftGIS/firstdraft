from os.path import dirname, realpath
from appfd.scripts.ai import train
#import tensorflow as tf
#from tensorflow.contrib.learn.python.learn import LinearClassifier
#from tensorflow.contrib.learn.python.learn import Estimator

classifier = train.run(return_classifier=True)
print("classifier:", classifier)

def run():
    try:
        print("starting ai.predict")

        #path_to_directory_of_this_file = dirname(realpath(__file__))
        #model_dir = path_to_directory_of_this_file + "/classifier"
        #classifier = LinearClassifier(feature_columns, model_dir=model_dir)
        #classifier = Estimator(model_dir=model_dir)
        #classifier.fit(max_steps=0)

    except Exception as e:
        print(e)


