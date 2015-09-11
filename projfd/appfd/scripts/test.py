# location extractor
# extracts locations from text
from bnlp import clean, getLocationsFromEnglishText
from bs4 import BeautifulSoup
from bscrp import *
from resolve import *


def run():
  text = open("/home/usrfd/firstdraft/projfd/appfd/scripts/tmp.txt").read()
  print type(text)
  if isWikipediaArticle(text):
    print "text is wikipedia article"
    text = BeautifulSoup(text).select("#bodyContent")[0].text
    print "type(text) is", type(text), len(text), dir(text)

    locations = getLocationsFromEnglishText(text)
    print "locations are", locations

    locations = [resolve(loc) for loc in locations]    

    print locations
