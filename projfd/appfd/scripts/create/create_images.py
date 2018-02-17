from appfd.models import Feature, FeaturePlace
from appfd.models import Order
from os import environ, mkdir, remove
from os.path import devnull, isdir, isfile
from selenium import webdriver
from time import sleep

def run(key):
    try:
        print("starting create_images with key " + key)

        from django.db import connection
        connection.close()

        directory = "/home/usrfd/maps/" + key + "/"
        if not isdir(directory):
            mkdir(directory)

        driver = webdriver.PhantomJS(service_log_path=devnull)
        #driver = webdriver.PhantomJS(service_args=["--remote-debugger-port=9000"], service_log_path=devnull)
        #driver = webdriver.PhantomJS(service_args=["--debug=True"], service_log_path=devnull)
        driver.set_window_size(1024, 768)

        # this assumes that you are running some sort of webserver like Apache2
        # if you're running FDGIS on another port, you will have to add in a port here
        driver.get("http://127.0.0.1/preview_map/" + key)

        # sleep 5 seconds to let basemap load
        sleep(5)

        for extension in ["gif", "jpg", "png"]:
            path_to_screenshot = directory + key + "." + extension
            print("path_to_screenshot:", path_to_screenshot)
            if isfile(path_to_screenshot): remove(path_to_screenshot) 
            driver.save_screenshot(directory + key + "." + extension)

        driver.quit()

        print("finished create_images")
    except Exception as e:
        print("CAUGHT EXCEPTION in create_images:", e)
