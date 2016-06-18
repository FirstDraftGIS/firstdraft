#environment.py
from pyvirtualdisplay import Display
from selenium import webdriver
from subprocess import check_output

def before_all(context):
    context.display = Display(visible=0, size=(1024, 600)).start()
    context.driver = webdriver.Firefox()
    #ip_address = gethostbyname(gethostname())
    ip_address = check_output("wget http://ipinfo.io/ip -qO -", shell=True)
    context.driver.get("http://" + ip_address)
    context.driver.save_screenshot("/tmp/scrn.png")

def after_all(context):
    context.driver.quit()
    context.display.stop()

