import location_extractor
from re import findall
from table import extract_locations_from_tables
from webpage import extract_locations_from_webpage


# we're just casting a wide net and extracting 
# all the capitalized words and other words that follow rules
def extract_locations_from_text(text):

    try:

        print "starting extract_locations_from_text"

        pattern = "(?:[A-Z][a-z]{1,15} )*(?:de )?[A-Z][a-z]{1,15}"
        names = [name for name in set(findall(pattern, text)) if len(name) > 3]
        location_extractor.load_non_locations()
        names = [name for name in names if name not in location_extractor.nonlocations]

        location_extractor.load_language_into_dictionary_of_keywords("English")
        for possible_abbreviation in list(set(findall("[A-Z]{2}", text))):
            print "possible_abbreviation:", possible_abbreviation
            print "keys:", location_extractor.dictionary_of_keywords['English']['abbreviations'].keys()
            #name = location_extractor.dictionary_of_keywords['English']['abbreviations'].get(possible_abbreviation, None)
            #if name:
            #    names.append({ "abbreviation": possible_abbreviation, "name": name })
            #if possible_abbreviation in location_extractor.dictionary_of_keywords['English']['abbreviations']:
            #    names.append(possible_abbreviation)

        print "names are yeah:", names

        results = location_extractor.extract_locations_with_context(text, names, debug=True, return_abbreviations=True)
        print "results:", results
        return results

    except Exception as e:
        print "EXCEPTION in extractor:", e
