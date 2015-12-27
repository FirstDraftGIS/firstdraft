from appfd.models import *
from bnlp import *
from bs4 import BeautifulSoup
from collections import Counter
from django.contrib.gis.gdal import DataSource
#from django.contrib.gis.gdal.geometries import Polygon
from django.contrib.gis.geos import MultiPolygon, Polygon, Point
#from location_extractor import extract_locations
from numpy import median
import os, urllib, zipfile
import shutil
from os import listdir, mkdir
from os.path import isdir, isfile
from requests import get, head
from subprocess import call
from urllib import urlretrieve, unquote
from bnlp import trim_location
from sys import exit

from django.utils.crypto import get_random_string


def find_shp_files_in_directory(path_to_directory):
    path_to_directory = path_to_directory.rstrip("/")
    paths_to_shps = []
    for filename in listdir(path_to_directory):
        try:
            path_to_file = path_to_directory + "/" + filename
            if isdir(path_to_file):
                paths_to_shps += find_shp_files_in_directory(path_to_file)
            elif isfile(path_to_file) and path_to_file.endswith(".shp"):
                paths_to_shps.append(path_to_file)
        except:
            pass
    return paths_to_shps

def describe_layer_fields(layer):
    fields = layer.fields
    field_types = [ft.__name__ for ft in layer.field_types]
    dictionary = {}
    for i, field in enumerate(fields):
        d = {}
        d['field_lower'] = field.lower()
        d['field_type'] = field_types[i]
        d['values_list'] = [value.lower() if isinstance(value, str) or isinstance(value, unicode) else value for value in layer.get_fields(field)]
        d['number_of_values'] = len(values_list)
        d['values_set'] = set(d['values_list'])
        d['completeness'] = float(len([value for value in d['values_list'] if value])) / float(len(d['values_list']))
        d['uniqueness'] = float(len(d['values_set'])) / float(len(d['values_list']))
        dictionary[field] = d
 
    return d


def get_name_field(layer, fields, field_types):
    print "starting get_name_field with:"
    print fields
    print field_types
    candidates = []
    for i, field in enumerate(fields):
        field = fields[i]
        field_lower = field.lower()
        field_type = field_types[i]
        values_list = [value.lower() if isinstance(value, str) or isinstance(value, unicode) else value for value in layer.get_fields(field)]
        number_of_values = len(values_list)
        values_set = set(values_list)
        number_of_unique_values = len(values_set)
        completeness = float(len([value for value in values_list if value])) / float(number_of_values)
        uniqueness = float(number_of_unique_values) / float(number_of_values)
        if field_type == "OFTString" and completeness > 0.4 and uniqueness > 0.4 and not isGibberish(values_set) and number_of_unique_values > 10:
            candidates.append((field, uniqueness))

    # sort candidates by uniqueness
    candidates = sorted(candidates, key = lambda candidate: -1*candidate[1])

    if len(candidates) > 0:
        print "returning ", candidates[0][0]
        return candidates[0][0]
         
    """
    admin_level = IntegerField(null=True, blank=True, db_index=True)
    admin1_code = CharField(max_length=100, null=True, blank=True, db_index=True)
    admin2_code = CharField(max_length=100, null=True, blank=True, db_index=True)
    aliases = ManyToManyField('Alias', through="AliasPlace", related_name="place_from_placealias+")
    area_sqkm = IntegerField(null=True, blank=True)
    country_code = CharField(max_length=2, null=True, blank=True, db_index=True)
    district_num = IntegerField(null=True, blank=True)
    fips = IntegerField(null=True, blank=True, db_index=True)
    geonameid = IntegerField(null=True, blank=True, db_index=True)
    mls = MultiLineStringField(null=True, blank=True)
    mpoly = MultiPolygonField(null=True, blank=True)
    name = CharField(max_length=200, null=True, blank=True, db_index=True)
    note = CharField(max_length=200, null=True, blank=True)
    objects = GeoManager()
    point = PointField(null=True, blank=True)
    population = BigIntegerField(null=True, blank=True)
    pcode = CharField(max_length=200, null=True, blank=True)
    skeleton = MultiLineStringField(null=True, blank=True)
    timezone = CharField(max_length=200, null=True, blank=True)
    """

   

def parse_layer(layer):
    print "starting parse_layer with ", layer

    fields = layer.fields
    field_types = [ft.__name__ for ft in layer.field_types]
    print "field_types are", field_types
    d = {}
#    fields = describe_layer_fields(layer)
    # aliases = []
    # alias/language
#    admin_level
    pcodes = []
#    for i, field in enumerate(fields):

    #d['name'] = get_name_field(fields)
    #print "d['name'] = ", d['name']

    for i, field in enumerate(fields):
        field = fields[i]
        print "field is", field
        field_lower = field.lower()
        field_type = field_types[i]
        values_list = [value.lower() if isinstance(value, str) or isinstance(value, unicode) else value for value in layer.get_fields(field)]
        number_of_values = len(values_list)
        values_set = set(values_list)
        number_of_unique_values = len(values_set)
        completeness = float(len([value for value in values_list if value])) / float(number_of_values)
        uniqueness = float(number_of_unique_values) / float(number_of_values)
 
        if "objectid" in field_lower:
            continue
        elif "leng" in field_lower:
            continue
        elif "area" in field_lower:
            d["area_sqkm"] = field
            continue
        elif "pcode" in field_lower or field_lower.endswith("_pc"):
            if completeness > 0.9 and uniqueness > completeness - 0.05:
                d["pcode"] = field
            else:
                pcodes.append((field,uniqueness))
            continue
        
        if len(values_set) <= 2 and ("region" in values_set) + ("state" in values_set) == 2:
            d['admin_level'] = field
            continue
 
        if field_type == "OFTString" and completeness > 0.8 and uniqueness > 0.8 and not isGibberish(values_set):
            d['name'] = field

            # if there is a name repeated in an ostensibly unique name column, don't use that name
            d['badnames'] = [name for name, count in Counter(values_list).most_common(20) if len(name) < 2]

            continue

    # if weren't able to get the name from the first pass
    # try again lowering the bar
    if "name" not in d:
        d['name'] = get_name_field(layer, fields, field_types)
        values_list = [value.lower() for value in layer.get_fields(d['name'])]
        d['badnames'] = [name for name, count in Counter(values_list).most_common(20) if len(name) < 2]
        #raw_input()


    if "admin_level" not in d:
        if "vill" in d['name'].lower():
            d['admin_level'] = 5

    if pcodes:
        # highest to lowest
        pcodes = sorted(pcodes, key=lambda tup: -1*tup[1])
        d['parent_pcode'] = [fieldname for fieldname, uniquenes in pcodes][0]

    print "d is", d
    return d

#def getCountryCode():
#write method maybe put into views or scripts or something so people can send in a shapefile can get a country code if it applies to more than 95% of a random sample of features


def download(url, path_to_directory):
    print "starting download with", url, path_to_directory
    if "geoserver/wfs" in url:
        filename = unquote(search("(?<=typename=)[^&]*",url).group(0)).replace(":","_")
        extension = "zip"
    else:
        filename, extension = unquote(url.split("?")[0].split("/")[-1]).split(".")
    print "filename is", filename
    print "extension is", extension
    path_to_directory_of_downloadable = path_to_directory + "/" + filename
    if not isdir(path_to_directory_of_downloadable):
        mkdir(path_to_directory_of_downloadable)
    path_to_downloaded_file = path_to_directory_of_downloadable + "/" + filename + "." + extension
    if not isfile(path_to_downloaded_file):
        urlretrieve(url, path_to_downloaded_file)
        print "saved file to ", path_to_downloaded_file
    if path_to_downloaded_file.endswith("zip"):         
        with zipfile.ZipFile(path_to_downloaded_file, "r") as z:
            z.extractall(path_to_directory_of_downloadable)


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
                filename, extension = unquote(path.split("?")[0].split("/")[-1]).split(".")
                path_to_directory = path_to_tmp + "/" + filename
                if not isdir(path_to_directory):
                    mkdir(path_to_directory)
                download(path, path_to_directory)
 
        elif content_type.startswith("text/html"):
            print "content-type is text/html"
            dirname = path.replace(".","_").replace("/","_").replace("-","_").replace(":","_").replace("___","_").replace("__","_")
            print "dirname is", dirname
            path_to_directory = path_to_tmp + "/" + dirname
            if not isdir(path_to_directory):
                mkdir(path_to_directory)
                print "made directory: ", path_to_directory
            soup = BeautifulSoup(get(path).text, "lxml")

            title = soup.title.text.lower()
            if "admin 1" in title:
                admin_level = 1
            elif "admin 2" in title:
                admin_level = 2
            elif "admin 3" in title:
                admin_level = 3
            elif "admin 4" in title:
                admin_level = 4
            elif "admin 5" in title:
                admin_level = 5

            downloadables = soup.select("a[href$=zip]")
            hrefs = [a['href'] for a in soup.select("a[href$=zip]")]
            for href in hrefs:
                download(href, path_to_directory)

    paths_to_shps = find_shp_files_in_directory(path_to_directory) 
    print "path_to_shps = ", paths_to_shps

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
    path_to_shp = filepath_no_ext + ".shp"
    print "path_to_shp = ", path_to_shp
    paths_to_shp = [path_to_shp]
    """
    for path_to_shp in paths_to_shps:
        print "for path_to_shp", path_to_shp
        #raw_input()

        if "adm1" in path_to_shp:
            admin_level = 1
        elif "adm2" in path_to_shp:
            admin_level = 2
        elif "adm3" in path_to_shp:
            admin_level = 3
        elif "adm4" in path_to_shp:
            admin_level = 4
        elif "adm5" in path_to_shp:
            admin_level = 5

        print "admin_level is", admin_level
        #raw_input()
        ds = DataSource(path_to_shp)
        print "ds is", ds
        print "dir(ds) = ", dir(ds)
        layers = list(ds)
        print "layers are", layers
        for layer in ds:
            print "layer is", layer
            print "dir(layer) is", dir(layer)
            print "layer.fields = ", layer.fields
            d = parse_layer(layer)
            badnames = d['badnames']
            #raw_input()
                  
            geom_type = str(layer.geom_type)
            features = list(layer)
            number_of_features = len(features)
            for i, feature in enumerate(features):
                try:
#                    if i % 500 != 0: continue
                    print "\nfor feature", i, "of", number_of_features
                    fields = {}

                    name = feature.get(d['name'])
                    if name and name.lower() not in badnames:
                        fields['name'] = name
                    else:
                        print name, " is not a good name, so skip over this feature"
                        continue

                    print "admin_level is", admin_level, "."
                    if admin_level:
                        print "got admin_level, so just use that"
                        fields['admin_level'] = admin_level
                    elif "admin_level" in d:
                        admin_level = feature.get(d['admin_level']) 
                        if isinstance(admin_level, str) or isinstance(admin_level, unicode):
                            if admin_level.isdigit():
                                admin_level = int(admin_level)
                            elif admin_level.lower() in ("region", "state"):
                                admin_level = 1

                    for key, value in d.iteritems():
                        if key not in ("admin_level","badnames","name","parent_pcode"):
                            print "\tfor key", key, "value", value
                            value = feature.get(value)
                            print "\tvalue = ", value
                            fields[key] = value 

                    geom = feature.geom.geos
                    if isinstance(geom, Polygon):
                        fields['mpoly'] = MultiPolygon([geom])
                        fields['point'] = geom.centroid
                    elif isinstance(geom, MultiPolygon):
                        fields['mpoly'] = geom
                        fields['point'] = geom.centroid
                    elif isinstance(geom, Point):
                        fields['point'] = geom
                    
                    print "geom_type = ", geom_type               

                    #need to load lsibwvs for country polygons
                    if "country_code" not in fields:
                        try:
                            fields['country_code'] = Place.objects.get(admin_level=0, mpoly__contains=fields['point']).country_code
                        except Exception as e:
                            print e

                    print "fields are", fields
                    place = Place.objects.get_or_create(**fields)[0]
                    if "parent_pcode" in d:
                        parent_pcode = feature.get(d['parent_pcode'])
                        print "parent_pcode is", parent_pcode
                        qs = Place.objects.filter(pcode=parent_pcode)
                        if qs.count() > 0:
                            parent = qs[0]
                            print "parent is", parent
                            ParentChild.objects.get_or_create(parent=parent, child=place)

                except Exception as e:
                    print "CAUGHT EXCEPTION on feature", i, "|", feature
                    print e
