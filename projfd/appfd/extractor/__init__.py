import location_extractor
from re import findall, IGNORECASE
from .table import extract_locations_from_tables
from .webpage import extract_locations_from_webpage

# http://locallyoptimal.com/blog/2013/01/20/elegant-n-gram-generation-in-python/
def find_ngrams(input_list, n):
  return [" ".join(ngram) for ngram in zip(*[input_list[i:] for i in range(n)])]

# we're just casting a wide net and extracting 
# all the capitalized words and other words that follow rules
def extract_locations_from_text(text, case_insensitive=None, debug=True):

    try:

        print("starting extract_locations_from_text")
        if debug:
            print("    [extractor] case_insensitive:", case_insensitive)

        pattern = "(?:[A-Z][a-z\u00ed]{1,15} )*(?:de )?[A-Z][a-z\u00ed]{1,15}"
        names = [name.lstrip("de ") for name in set(findall(pattern, text)) if len(name) > 3]
        if case_insensitive:
            names = [name.lstrip("de ") for name in set(findall(pattern, text, IGNORECASE)) if len(name) > 3]
        try: print("    [extractor] names from pattern:", [names])
        except: pass
        location_extractor.load_non_locations()
        nonlocations = [location.lower() for location in location_extractor.nonlocations]
        names = [name for name in names if name.lower() not in nonlocations]
        try: print("    names after filtering out nonlocations:", names)
        except: pass

        location_extractor.load_language_into_dictionary_of_keywords("English")
        for possible_abbreviation in list(set(findall("[A-Z]{2}", text))):
            print("possible_abbreviation:", possible_abbreviation)
            print("keys:", list(location_extractor.dictionary_of_keywords['English']['abbreviations'].keys()))
            #name = location_extractor.dictionary_of_keywords['English']['abbreviations'].get(possible_abbreviation, None)
            #if name:
            #    names.append({ "abbreviation": possible_abbreviation, "name": name })
            #if possible_abbreviation in location_extractor.dictionary_of_keywords['English']['abbreviations']:
            #    names.append(possible_abbreviation)

        # doing this because sometimes get grammatically incorrect tweets
        text_length = len(text)
        if text_length < 1e5:
            splat = text.split()
            names.extend([word.strip().strip(",").strip(";").strip(".")  for word in splat])

            if text_length < 500:
                names.extend([ngram.strip().strip(",").strip(";").strip(".") for ngram in find_ngrams(splat, 2)])

        #filter out nonlocations again
        names = [name for name in names if name.lower() not in nonlocations and len(name) > 3]

        # remove duplicates
        names = list(set(names))

        try: print("names are yeah:", names)
        except: pass

        results = location_extractor.extract_locations_with_context(text, names, debug=True, return_abbreviations=True, case_insensitive=case_insensitive)

        try: print("results:", results)
        except: pass

        return results

    except Exception as e:
        print("EXCEPTION in extractor:", e)
