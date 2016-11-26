from appfd.models import *
from bnlp import *
from bs4 import BeautifulSoup
from collections import Counter
import django
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.gdal.prototypes import ds as capi
#from django.contrib.gis.gdal.geometries import Polygon
from django.contrib.gis.geos import MultiPoint, MultiPolygon, Polygon, Point
from django.contrib.gis.measure import D
from django.utils.encoding import DjangoUnicodeDecodeError
from django.utils.encoding import force_text
#from location_extractor import extract_locations
from language_detector import detect_language
from numpy import median
import os, urllib, zipfile
import shutil
from os import listdir, mkdir, remove
from os.path import isdir, isfile
from pyproj import Proj, transform
from re import search as re_search
from random import shuffle
from requests import get, head
from subprocess import call
from urllib import urlretrieve, unquote
from urlparse import urlparse
from bnlp import trim_location
from super_python import *
from sys import exit
from zipfile import is_zipfile

from django.utils.crypto import get_random_string

def get_matching_place(fields):
    print "\nstarting get_matching_place with", fields
    # look up place and see if one is nearby or whatever
    matches_via_name_and_cc = Place.objects.filter(name=fields['name'], country_code=fields['country_code'])
    if matches_via_name_and_cc:
        print "\tmatches via name and country code:", matches_via_name_and_cc

        # match via same exact point
        matches_via_point = matches_via_name_and_cc.filter(point=fields['point'])
        if matches_via_point:
            print "\tmatches_via_point:", matches_via_point
            if fields['admin_level']:
                matches_via_admin_level = matches_via_point.filter(admin_level=fields['admin_level'])
                if matches_via_admin_level:
                    print "\tmatches_via_admin_level:", matches_via_admin_level
                    return matches_via_admin_level[0]
            else:
                matches_with_admin_level_3 = matches_via_point.filter(admin_level=3)
                if matches_with_admin_level_3:
                    return matches_with_admin_level_3[0]
                else:
                    return matches_via_point[0]

        if 'mpoly' in fields and fields['mpoly']:
            matches_inside_mpoly = matches_via_name_and_cc.filter(point__within=fields['mpoly'])
            if matches_inside_mpoly:
                print "\tmatches inside mpoly:", matches_inside_mpoly
                if 'admin_level' in fields and fields['admin_level']:
                    matches_via_admin_level = matches_inside_mpoly.filter(admin_level=fields['admin_level'])
                    if matches_via_admin_level:
                        print "\tmatches_via_admin_level:", matches_via_admin_level
                        return matches_via_admin_level[0]
                print "should return whichever one is closest to the point"
                return matches_inside_mpoly.distance(fields['point']).order_by('distance')[0]

        matches_via_distance = matches_via_name_and_cc.filter(point__distance_lt=(fields['point'], D(m=5)))
        if matches_via_distance:
            print "matches_via_distance:", matches_via_distance
            if "admin_level" in fields and fields['admin_level']:
                matches_via_admin_level = matches_inside_mpoly.filter(admin_level=fields['admin_level'])
                if matches_via_admin_level:
                    print "\tmatches_via_admin_level:", matches_via_admin_level
                    return matches_via_admin_level.distance(fields['point']).order_by('distance')[0]
            else:
                matches_with_admin_level_3 = matches_via_point.filter(admin_level=3)
                if matches_with_admin_level_3:
                    return matches_with_admin_level_3.distance(fields['point']).order_by("distance")
                else:
                    return matches_via_distance.distance(fields['point']).order_by('distance')

        # should probably do something with levenstein distance filter and edit distance filter

        
    print "no matches"

def get_values_list(layer, field, max_errors=0.05):
    number_of_features = len(layer)
    values = []
    errors = 0
    for feature in layer:
        #value = feature[field]
        try:
            value = feature.get(field)
        except DjangoUnicodeDecodeError as e:
            errors += 1
            continue
            """
            for encoding in ["utf-8", "ISO8859", "CP1251"]:
                #feature._encoding = encoding
                value = feature[field]
                setattr(value._feat, "encoding", encoding)
                value["_feat.encoding"] = value["_feat.encoding"]._replace(v=encoding)
                value = value.as_string()
                print "value:", value
                raw_input()
        #        try:
        #            value = force_text(string, encoding=self._feat.encoding, strings_only=True)
        #        except Exception as e:
        #            print e
        print "value:", value
           """
        if isinstance(value, str):
            value.append(value.decode("utf-8").lower())
        elif isinstance(value, unicode):
            values.append(value.lower())
        else:
            values.append(value)
    if 0 < max_errors < 1 and float(errors)/number_of_features > max_errors:
        raise Exception("Hit Max Errors on get_values_list")

    return values
 


def get_admin_level_from_string(string):
    print "starting get_ad...", string
    string_lower = string.lower()
    if any([text in string_lower for text in ["admin 1", "admin1", "adm1", "shabiya"] ]):
        return 1
    elif any([text in string_lower for text in ["admin 2", "admin2", "adm2"] ]):
        return 2
    elif any([text in string_lower for text in ["admin 3", "admin3", "adm3"] ]):
        return 3
    elif any([text in string_lower for text in ["admin 4", "admin4", "adm4"] ]):
        return 4
    elif any([text in string_lower for text in ["admin 5", "admin5", "adm5", "vill", "village", "hay"] ]):
        return 5

def find_gis_files_in_directory(path_to_directory):
    path_to_directory = path_to_directory.rstrip("/")
    paths_to_gis_files = []
    for filename in listdir(path_to_directory):
        try:
            path_to_file = path_to_directory + "/" + filename
            # gdb files are treated as directories by python, so we need to override this by checking if ends with gdb
            if (isfile(path_to_file) and path_to_file.endswith(".shp")) or path_to_file.endswith(".gdb"):
                paths_to_gis_files.append(path_to_file)
            elif isdir(path_to_file):
                paths_to_gis_files += find_gis_files_in_directory(path_to_file)
        except:
            pass
    return paths_to_gis_files

def describe_layer_fields(layer):
    fields = layer.fields
    field_types = [ft.__name__ for ft in layer.field_types]
    dictionary = {}
    for i, field in enumerate(fields):
        d = {}
        d['field_lower'] = field.lower()
        d['field_type'] = field_types[i]
        d['values_list'] = get_values_list(layer, field)
        d['number_of_values'] = len(values_list)
        d['values_set'] = set(d['values_list'])
        d['completeness'] = float(len([value for value in d['values_list'] if value])) / float(len(d['values_list']))
        d['uniqueness'] = float(len(d['values_set'])) / float(len(d['values_list']))
        dictionary[field] = d
 
    return d

@superfy
def get_area_field(layer, fields, field_types):
    print fields
    print field_types
    candidates = []
    for i, field in enumerate(fields):
        field = fields[i]
        field_lower = field.lower()
        field_type = field_types[i]
        if field_type == "OFTReal" and any(word in field_lower for word in ["area","sqkm","sqkm","km2","km_2"]):
            values_list = get_values_list(layer, field)
            values_median = median(values_list)

            # we certainly don't want this if the median
            if values_median > 0:
                candidates.append((field, values_median))

    # sort candidates by median
    candidates = sorted(candidates, key = lambda candidate: -1*candidate[1])

    if number_of_candidates == 0:
        return None
    elif number_of_candidates == 1:
        return candidates[0][0]
    elif number_of_candidates > 0:
        sqkms = [c for c in candidates if re_search("(km2|sqkm|sq_km)", c[0].lower())]
        if number_of_sqkms == 0:
            return candidates[0][0]
        else:
            return sqkms[0][0]

def isPcodeValue(string):
     return match("[A-Za-z]{2}\d{2,}", string)

# could this value plausibly be a part of a name field
def isNameValue(string):
    if isGibberish(string):
        return False
    elif isPcodeValue(string):
        return False
    elif string.isdigit():
        return False
    return True

def isNameList(lst):
    length = len(lst)
    count = 0
    for string in lst:
        count += isNameValue(string)
    percentage = float(count) / float(length)
    return percentage > 0.7



def get_name_field(layer, fields, field_types, min_completeness=0.8, min_uniqueness=0.8):
    names_of_fields = get_name_fields(layer, fields, field_types, min_completeness, min_uniqueness)[0]

    # remove any name fields that are for Arabic, but if that removes all of them
    # then just use Arabic
    names_of_fields = [name for name in names_of_fields if not name.lower().endswith("ar")] or names_of_fields

    return names_of_fields[0]

# because there can be multiple columns with names in it
# we have to figure out which column is the primary name (aka name) and which are 
# "other names" aka aliases
def get_name_and_alias_fields(layer, fields, field_types):

    # tries to get the fields with a cutoff of 0.8 in completeness and uniqueness
    # if that doesn't work, try again using a cutoff of 0.4
    name_fields = get_name_fields(layer, fields, field_types) or get_name_fields(layer, fields, field_types, min_completeness=0.4, min_uniqueness=0.4)

    if name_fields:
        name_fields_in_english = [name_field for name_field in name_fields if name_field['language'] == "English"]
        print "name_fields_in_english = ", name_fields_in_english
        primary_name_field = name_fields_in_english[0] if name_fields_in_english else name_fields[0]
        primary_name = primary_name_field['name']
        alias_fields = [name_field for name_field in name_fields if name_field != primary_name_field]

        return primary_name, alias_fields
    else:
        return None, []

@superfy
def get_name_fields(layer, fields, field_types, min_completeness=0.8, min_uniqueness=0.8):
    print "starting get_name_field with:"
    print fields
    print field_types
    name_fields = []
    for i, field in enumerate(fields):
        field = fields[i]
        field_lower = field.lower()
        field_type = field_types[i]
        values = get_values_list(layer, field)
        values_set = set(values)
        number_of_unique_values = len(values_set)
        completeness = float(len([value for value in values if value])) / float(number_of_values)
        uniqueness = float(number_of_unique_values) / float(number_of_values)
        if "pc" not in field_lower and field_type == "OFTString" and completeness > min_completeness and uniqueness > min_uniqueness and not isGibberish(values_set) and number_of_unique_values > 10 and isNameList(values_set):
            language = detect_language(values)
            name_fields.append({"name": field, "uniqueness": uniqueness, "language": language})

    # sort namefields by uniqueness
    name_fields = sorted(name_fields, key = lambda namefield: -1*namefield["uniqueness"])

    print "name_fields are", name_fields
    return name_fields


def parse_layer(layer):
    print "starting parse_layer with ", layer

    fields = layer.fields
    field_types = [ft.__name__ for ft in layer.field_types]
    print "field_types are", field_types
    d = {}
    pcodes = []

    d['admin_level'] = get_admin_level_from_string(layer.name)

    area_sqkm = get_area_field(layer, fields, field_types)
    if area_sqkm:
        d['area_sqkm'] = area_sqkm

    if layer.num_feat <= 10:
        for potential_name in ["NOMBRE", "name"]:
            if potential_name in fields:
                d["name"] = potential_name
                d["aliases"] = []
                break
    else:
        d["name"], d['aliases'] = get_name_and_alias_fields(layer, fields, field_types)
    

    for i, field in enumerate(fields):
        field = fields[i]
        print "field is", field
        field_lower = field.lower()
        field_type = field_types[i]
        values_list = get_values_list(layer, field)
        number_of_values = len(values_list)
        values_set = set(values_list)
        number_of_unique_values = len(values_set)
        completeness = float(len([value for value in values_list if value])) / float(number_of_values)
        uniqueness = float(number_of_unique_values) / float(number_of_values)
 
        if "objectid" in field_lower:
            continue
        elif "leng" in field_lower:
            continue
        elif "pcode" in field_lower or field_lower.endswith("_pc"):
            if completeness > 0.9 and uniqueness > completeness - 0.05:
                d["pcode"] = field
            else:
                pcodes.append((field,uniqueness))
            continue
        
        if len(values_set) <= 2 and ("region" in values_set) + ("state" in values_set) == 2:
            d['admin_level'] = 1
            continue

    if "admin_level" not in d:
        admin_level = get_admin_level_from_string((d['name'] or "").lower())
        if admin_level:
            d['admin_level'] = admin_level

    if pcodes:
        # highest to lowest
        pcodes = sorted(pcodes, key=lambda tup: -1*tup[1])
        d['parent_pcode'] = [fieldname for fieldname, uniquenes in pcodes][0]

    print "d is", d
    return d

def get_country_code_from_shuffled_features(features):
    country_codes = set()
    for feature in features[:20]:
        geom = feature.geom
        geom.transform(u'+proj=longlat +datum=WGS84 +no_defs ')
        geos = geom.geos
        if isinstance(geos, Point):
            point = geos
        elif isinstance(geos, Polygon) or isinstance(geos, MultiPolygon):
            point = geos.centroid
        elif isinstance(geos, MultiPoint):
            point = geos[0]
        place = Place.objects.filter(admin_level=0, mpoly__contains=point).first()
        if place:
            country_codes.add(place.country_code)

    if len(country_codes) == 1:
        return country_codes.pop()

def download(url, path_to_directory):
    print "starting download with", url, path_to_directory
    if "geoserver/wfs" in url:
        filename = unquote(search("(?<=typename=)[^&]*",url).group(0)).replace(":","_")
        extension = "zip"
        filename_with_extension = filename + "." + extension
    else:
        filename_with_extension = unquote(url.split("?")[0].split("/")[-1])
        print "filename_with_extension = ", filename_with_extension
        filename = filename_with_extension.split(".")[0]
        
    print "filename is", filename
    print "filename_with_extension = ", filename_with_extension
    path_to_directory_of_downloadable = path_to_directory + "/" + filename
    if not isdir(path_to_directory_of_downloadable):
        mkdir(path_to_directory_of_downloadable)
    path_to_downloaded_file = path_to_directory_of_downloadable + "/" + filename_with_extension
    if not isfile(path_to_downloaded_file):
        print "url:", url
        print "path_to_downloaded_file:", path_to_downloaded_file
        urlretrieve(url, path_to_downloaded_file)
        print "saved file to ", path_to_downloaded_file
    if path_to_downloaded_file.endswith("zip"):         
        if is_zipfile(path_to_downloaded_file):    
            with zipfile.ZipFile(path_to_downloaded_file, "r") as z:
                z.extractall(path_to_directory_of_downloadable)
                print "unzipped", path_to_downloaded_file
        else:
            remove(path_to_downloaded_file)
            print "removed file because it wasn't a zip file eventhough had zip extension"

@superfy
def run(path):
    print "starting load.run with ", path
    admin_level = None
    country_code = None

    path_to_tmp = "/tmp"


    #clear the tmp directory
    call(["rm","-fr","/tmp/*"])

    paths_to_shps = []

    if path.startswith("http"):
        content_type = head(path).headers['content-type']
        print "content_type = ", content_type
        if content_type == "application/zip":
            print "content-type is application/zip"
            if "geoserver/wfs" in path:
                dirname = unquote(search("(?<=typename=)[^&]*",path).group(0)).replace(":","_")
                print "dirname is", dirname
                extension = "zip"
                path_to_directory = path_to_tmp + "/" + dirname
                print "path_to_directory is", path_to_directory
                if not isdir(path_to_directory):
                    mkdir(path_to_directory)
                download(path, path_to_directory)
            elif path.endswith(".zip"):
                print "zip"
                filename = unquote(path.split("?")[0].split("/")[-1]).split(".")[0]
                path_to_directory = path_to_tmp + "/" + filename
                if not isdir(path_to_directory):
                    mkdir(path_to_directory)
                download(path, path_to_directory)
 
        elif content_type.startswith("text/html"):
            print "content-type is text/html"
            dirname = path.replace(".","_").replace("/","_").replace("-","_").replace(":","_").replace("___","_").replace("__","_")
            print "dirname is", dirname
            path_to_directory = path_to_tmp + "/" + dirname
            print "path_to_directory is", path_to_directory
            if not isdir(path_to_directory):
                mkdir(path_to_directory)
                print "made directory: ", path_to_directory
            text = get(path).text
            print "text is", type(text), len(text)
            soup = BeautifulSoup(text, "lxml")
            print "soup is", type(soup)

            if soup.title:
                title = soup.title.text.lower()
                admin_level = get_admin_level_from_string(title)

            # can be set to None if none found

            domain = None
            hrefs = [a['href'] for a in soup.select("a[href$=zip]")]
            for href in hrefs:
                if not href.startswith("http"):
                    if not domain:
                        parsed = urlparse(path)
                        domain = parsed.scheme + "://" + parsed.netloc
                    href = domain + href
                download(href, path_to_directory)

    paths_to_gis_files = find_gis_files_in_directory(path_to_directory) 
    print "path_to_gis_files = ", paths_to_gis_files

    """
    if path.startswith("http"):
        print "passed in a urle(
        url = path
        #filename, extension = ".".join(url.split(".")[-2:]).split("/")[-1]
        filename, extension = url.split("/")[-1].split(".")[-2:]
        print "filename is", filename
        print "extension is", extension


        path_to_dir = "/tmp/" + filename
        if not isdir(path_to_dir):
            mkdir(path_to_dir)

        filepath = path_to_dir + "/" + filename + "." + extension
        if not isfile(filepath):
            urlretrieve(url, filepath)



    else:
         filepath = path
   
    if filepath.endswith("zip"):         
        print filepath, "ends wi zip"
        with zipfile.ZipFile(filepath, "r") as z:
            z.extractall('/tmp/')

    filepath_no_ext = "".join(filepath.split(".")[:-1])  
    path_to_gis_file = filepath_no_ext + ".shp"
    print "path_to_gis_file = ", path_to_gis_file
    paths_to_shp = [path_to_gis_file]
    """
    for path_to_gis_file in paths_to_gis_files:
        print "for path_to_gis_file", path_to_gis_file
        #raw_input("press any key to continue")

        # can be None if none found
        admin_level = get_admin_level_from_string(path_to_gis_file)
        print "admin_level is", admin_level
        ds = DataSource(path_to_gis_file)
        print "ds is", ds
        print "dir(ds) = ", dir(ds)
        layers = list(ds)
        print "layers are", [str(layer) for layer in layers]
        layer_parsing = [(layer, parse_layer(layer)) for layer in layers]

        # we want to sort the layers by admin level
        # we add the top-level parents in first,
        # so we can link a new feature to its existing parent
        layer_parsing = sorted(layer_parsing, key = lambda tup: tup[1]['admin_level'])

        for layer, d in layer_parsing:
            print "layer is", layer
            #raw_input()
            print "dir(layer) is", dir(layer)
            print "layer.fields = ", layer.fields

            if "name" not in d or not d['name']:
                print "couldn't get name layer, so skip over this layer"
                continue
            else: print "successfully got name", d['name']
            #raw_input()

            if 'admin_level' in d and d['admin_level']:
                admin_level = d['admin_level']

            geom_type = str(layer.geom_type)
            features = list(layer)
            shuffle(features)


            country_code = get_country_code_from_shuffled_features(features)
            places_added = []
            for i, feature in enumerate(features):
                try:

                    print "\nfor feature", i, "of", number_of_features
                    fields = {'admin_level': admin_level}

                    print "d['name'] = ", d['name']
                    name = feature.get(d['name'])
                    print "name is", name
                    if len(name) > 2:
                        fields['name'] = name
                    else:
                        continue
                    

                    #print "admin_level is", admin_level, "."
                    #if "admin_level" in d:
                    #    admin_level = feature.get(d['admin_level']) 
                    #    if isinstance(admin_level, str) or isinstance(admin_level, unicode):
                    #        if admin_level.isdigit():
                    #            admin_level = int(admin_level)
                    #        elif admin_level.lower() in ("region", "state"):
                    #            admin_level = 1

                    for key, value in d.iteritems():
                        if key not in ("admin_level","aliases","badnames","name","names","parent_pcode"):
                            print "\tfor key", key, "value", value
                            value = feature.get(value)
                            print "\tvalue = ", value
                            fields[key] = value 

                    geom = feature.geom
                    geom.transform(u'+proj=longlat +datum=WGS84 +no_defs ')
                    geos = geom.geos
                    # transforms the geom to lat lon if necessary; if already longlat, nothing happens
                    print "\tgeom_type = ", geom_type
                    if isinstance(geos, Polygon):
                        fields['mpoly'] = MultiPolygon([geos])
                        fields['point'] = geos.centroid
                        print "centroid is", geos.centroid
                    elif isinstance(geos, MultiPolygon):
                        fields['mpoly'] = geos
                        fields['point'] = geos.centroid
                    elif isinstance(geos, MultiPoint):
                        print "MultiPoint geos:", geos
                        print "points", list(geos)
                        if len(geos) == 1:
                            fields['point'] = geos[0]
                        else:
                            fields['point'] = geos[0]
                    elif isinstance(geos, Point):
                        fields['point'] = geos
                    

                    #need to load lsibwvs for country polygons
                    if country_code:
                        if "country_code" not in fields:
                            fields['country_code'] = country_code
                    else:
                        if "country_code" not in fields:
                            try:
                                fields['country_code'] = cc = Place.objects.get(admin_level=0, mpoly__contains=fields['point']).country_code
                                country_codes.add(cc)
                            except Exception as e:
                                print e
                    #raw_input()
                            
                    place = get_matching_place(fields)
                    print "get_matching_place returned:", place
                    if not place:
                        place = Place.objects.create(**fields)
                        print "created place", place

                    if "parent_pcode" in d:
                        parent_pcode = feature.get(d['parent_pcode'])
                        print "parent_pcode is", parent_pcode
                        parent = Place.objects.filter(pcode=parent_pcode).first()
                        if parent:
                            print "parent is", parent
                            ParentChild.objects.get_or_create(parent=parent, child=place)

                    for dic in d['aliases']:
                        aliasString = feature.get(dic['name'])
                        language = dic['language']
                        qs = Alias.objects.filter(alias=aliasString)
                        if qs.count() == 0:
                            alias = Alias.objects.create(alias=aliasString, language=language)
                            print "created alias", alias.id
                        else:
                            alias = qs[0]
                            alias.update({"language":language})
                        AliasPlace.objects.get_or_create(alias=alias, place=place)[0]
                        print "created AliasPlace", alias, place
                    places_added.append(place)


                except Exception as e:
                    print "CAUGHT EXCEPTION on feature", i, "|", feature
                    print e
                    #raw_input()
