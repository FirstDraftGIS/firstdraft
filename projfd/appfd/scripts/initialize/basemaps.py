from appfd.models import Basemap
from os.path import devnull
from re import search
from selenium import webdriver
from time import sleep

#initializes basemaps
def run():

    try:

        ignore_these_keys = ["CartoDB", "Esri", "HERE", "MapBox"]


        driver = webdriver.PhantomJS(service_log_path=devnull)    

        with open("/home/usrfd/firstdraft/projfd/static/node_modules/leaflet/dist/leaflet-src.js") as f:
            driver.execute_script(f.read())

        with open("/home/usrfd/firstdraft/projfd/static/node_modules/leaflet-providers/leaflet-providers.js") as f:
            driver.execute_script(f.read())

        print "current_url:", driver.current_url

        providers = driver.execute_script("return L.TileLayer.Provider.providers")

        #print "providers:", providers

        for key in providers:

            if key not in ignore_these_keys:

                value = providers[key]

                if "variants" in value:
                    for variant in value['variants']:
                        #print "name: " + key +"."+ variant
                        name = key + "." + variant
 
                        Basemap.objects.create(name=name)

                #else:
                #    print 'x:', value

    except Exception as e:
        print e
