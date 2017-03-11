from bnlp import clean as bnlp_clean
from broth import Broth
from location_extractor import extract_locations_with_context, extract_locations_with_context_from_html_tables
from newspaper import Article
from scrp import getTextContentViaMarionette, getRandomUserAgentString
from requests import get

def extract_locations_from_webpage(url, html=None, max_seconds=5):
  try:

    filename = url.replace("/","_").replace("\\","_").replace("'","_").replace('"',"_").replace(".","_").replace(":","_").replace("__","_")

    if not html:
        headers = {"User-Agent": getRandomUserAgentString()}
        html = get(url, headers=headers).text

    article = Article(url)
    article.download()
    article.parse()
    if article.text > 500:
        text = article.text
        print "got text using newspaper"
    else:
        headers = {"User-Agent": getRandomUserAgentString()}
        text = bnlp_clean(html)


    locations = extract_locations_with_context_from_html_tables(html)
    names_from_tables = [location['name'] for location in locations]

    for location in extract_locations_with_context(text, ignore_these_names=names_from_tables, debug=False, max_seconds=max_seconds-2):
        name = location['name']
        skip = False
        for l in locations:
            if name == l['name']:
                skip = True
        if not skip:
            locations.append(location)


    if not locations:
        print "no features, so try with selenium"
        text = getTextContentViaMarionette(url)
        locations = extract_locations_with_context(html)
 

    return locations

  except Exception as e:
    print "Caught Exception in extract_locations_from_webpage:", e