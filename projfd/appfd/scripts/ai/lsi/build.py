from appfd.models import Feature, Place, Topic
from collections import Counter
from datetime import datetime
from date_extractor import month_to_number
from gensim.corpora import Dictionary, MmCorpus
from gensim.models.ldamodel import LdaModel
from gensim.models.lsimodel import LsiModel
from gensim.similarities import MatrixSimilarity
from nltk.corpus import stopwords as nltk_stopwords
from os.path import dirname, realpath
from re import findall

path_to_directory_of_this_file = dirname(realpath(__file__))

stopwords = []
stopwords += [month.lower() for month in list(month_to_number.keys())]
stopwords += nltk_stopwords.words('english')
#print "stopwords:", len(stopwords)
with open(path_to_directory_of_this_file + "/stopwords.txt") as f:
    stopwords.extend([word for word in f.read().decode("utf-8").split("\n") if word and not word.startswith("#")])
stopwords = set(stopwords)

def prettify_topic(string):

    topics = findall('(?<=")[^"\d]+(?=")', string)

    result = ""
    number_of_topics = len(topics)
    if number_of_topics == 1:
        return topics[0]
    elif number_of_topics == 2:
        return topics[0] + " and " + topics[1]
    elif number_of_topics >= 3:
        return topics[0] + ", " + topics[1] + " and " + topics[2]

def tokenize(text):
    #print "starting tokenize with", text
    result = [word for word in text.lower().replace("#"," ").replace("_"," ").replace("("," ").replace(")"," ").replace("/"," ").replace(":"," ").replace("."," ").split() if word not in stopwords and 3 < len(word) < 15 ]
    #print "finishing tokenize with", result
    return result

def run():
  try:
    print("starting to build LSI Model")

    start = datetime.now()
    documents = Feature.objects.exclude(text=None).values_list("text", flat=True)
    number_of_documents = len(documents)
    print("number_of_documents:", number_of_documents)

    texts = [tokenize(document) for document in documents]

    counter = Counter()
    for text in texts:
        counter.update(text)

    texts = [[token for token in text if counter[token] > 1] for text in texts]

    print("texts:", len(texts), texts[:5])

    dictionary = Dictionary(texts)
    #print "dictionary:", dictionary
    dictionary.save(path_to_directory_of_this_file + "/dictionary")

    corpus = [dictionary.doc2bow(text) for text in texts]
    print("corpus:", type(corpus))

    print("generating lsi model")
    
    lsi = LsiModel(corpus=corpus, id2word=dictionary, num_topics=10)
    print("saving LSI model")
    lsi.save(path_to_directory_of_this_file + "/model")


    # nullifyin all topics on features and places
    Feature.objects.exclude(topic=None).update(topic=None)
    Place.objects.exclude(topic=None).update(topic=None)

    Topic.objects.all().delete()
    print("deleted all topics")
    topics = []
    for topic in lsi.show_topics():
        topics.append(Topic(id=topic[0], name=prettify_topic(topic[1])))

    Topic.objects.bulk_create(topics)
    print("bulk created all topics")


    """
    # re-create topics for all features in database
    for feature in Feature.objects.exclude(text=None).exclude(text=""):
        words = tokenize(feature.text)
        if words:
            probabilities = lsi[dictionary.doc2bow(words)]
            if probabilities:
                topic_id = sorted(probabilities, key=lambda tup: -1*tup[1])[0][0]
                if topic_id:
                    feature.topic_id = topic_id
                    feature.save()

    # assign as topic to each place based on most popular topic found in features
    for place_id in Place.objects.exclude(featureplace=None).values_list("id", flat=True):
        counter = Counter(Feature.objects.filter(featureplace__place_id=place_id).values_list("topic_id"))
        print "counter:", counter
    """


  except Exception as e:
    print(e)
