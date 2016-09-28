from datetime import datetime
from date_extractor import month_to_number
from gensim.corpora import Dictionary
from gensim.models.lsimodel import LsiModel
from nltk.corpus import stopwords as nltk_stopwords
from os.path import dirname, realpath

path_to_directory_of_this_file = dirname(realpath(__file__))

stopwords = []
with open(path_to_directory_of_this_file + "/stopwords.txt") as f:
    stopwords.extend([word for word in f.read().decode("utf-8").split("\n") if word and not word.startswith("#")])   
stopwords = set(stopwords)

lsi = LsiModel.load(path_to_directory_of_this_file + "/model")
   
dictionary = Dictionary.load(path_to_directory_of_this_file + "/dictionary")

def run(text):

    try:

        words = text.lower().replace("#"," ").replace("_"," ").replace("("," ").replace(")"," ").replace("/"," ").replace(":"," ").replace("."," ").split()
        words = [word for word in words if len(word) > 3 and word not in stopwords]

        if words:
            probabilities = lsi[dictionary.doc2bow(words)]
            if probabilities:
                return sorted(probabilities, key=lambda tup: -1*tup[1])[0][0]

    except Exception as e:
        print e
