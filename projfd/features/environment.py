#environment.py
from datetime import datetime
from pyvirtualdisplay import Display
from selenium import webdriver
from subprocess import call, check_output
from time import sleep

def before_all(context):

    context.start = datetime.now()

    call( [ "killall", "-9", "firefox" ] ) 

    context.display = Display(visible=0, size=(1024, 600)).start()
    sleep(5)

    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference("browser.download.folderList", 2)
    firefox_profile.set_preference("browser.download.manager.showWhenStarting", False)
    firefox_profile.set_preference("browser.download.dir", '/tmp')
    firefox_profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/csv,application/force-download,application/pdf,application/x-gzip,text/csv,text/plain")

    context.driver = webdriver.Firefox(firefox_profile=firefox_profile)

    #ip_address = gethostbyname(gethostname())
    ip_address = check_output("wget http://ipinfo.io/ip -qO -", shell=True)
    print ("ip_address: " + ip_address)
    context.driver.get("http://" + ip_address)
    context.driver.save_screenshot("/tmp/scrn.png")

def after_all(context):
    context.driver.quit()
    context.display.stop()
    print("took", (datetime.now()-context.start).total_seconds(), "seconds")
