from appfd.models import Feature, FeaturePlace
from appfd.models import Order
from os import environ, mkdir, remove
from os.path import devnull, isdir, isfile
from selenium import webdriver
from time import sleep

def run(key):
    try:
        print "starting create_pdf with key " + key

        from django.db import connection
        connection.close()

        directory = "/home/usrfd/maps/" + key + "/"
        if not isdir(directory):
            mkdir(directory)

        def execute(script, args):
            driver.execute('executePhantomScript', {'script': script, 'args' : args })

        driver = webdriver.PhantomJS(service_log_path=devnull)
        #driver = webdriver.PhantomJS(service_args=["--remote-debugger-port=9000"], service_log_path=devnull)
        #driver = webdriver.PhantomJS(service_args=["--debug=True"], service_log_path=devnull)
        height = 450
        width = 640
        driver.set_window_size(width, height)

        driver.command_executor._commands['executePhantomScript'] = ('POST', '/session/$sessionId/phantom/execute')

        # this assumes that you are running some sort of webserver like Apache2
        # if you're running FDGIS on another port, you will have to add in a port here
        driver.get("http://127.0.0.1/preview_map/" + key)

        # sleep 10 seconds to let leaflet and basemap load
        sleep(15)

        path_to_pdf = directory + key + ".pdf"
        print "path_to_pdf:", path_to_pdf
        if isfile(path_to_pdf): remove(path_to_pdf) 

        driver.execute_script("$('#map').height(" + str(height) + ").width(" + str(width) + ").css('position', 'relative');")
        sleep(2)
        print "set map height, width and position"
        driver.execute_script("map.fitBounds(featureGroup.getBounds().pad(0.01));")
        sleep(2)
        print "fit map"

        pageFormat = '''this.paperSize = {format: "Letter", margin: "1in", orientation: "landscape" };'''
        execute(pageFormat, [])

        render = '''this.render("'''+ path_to_pdf + '''")'''
        execute(render, [])

        print "rendered"

        driver.quit()

        print "finished create_pdf"
    except Exception as e:
        print "CAUGHT EXCEPTION in create_pdf:", e
