from appfd.models import Place
from selenium import webdriver
from time import sleep
import socket

#@then(u'The number of places should be greater than 10 million')
#def check_number_of_places(context):
#    assert(Place.objects.count() > 10000000)
@when("we visit the website")
def visit_the_website(context):
    ip_address = socket.gethostbyname(socket.gethostname()) 
    context.driver.get("https://" + ip_address)
 
@when("we open our browser")
def open_our_browser(context):
    context.driver = webdriver.Firefox()

@when("we start with a link to {url}")
def start_with_a_link(context, url):
    print("url:", url)
    context.driver.find_element_by_css_selector("input[value=url_to_webpage]").click()
    context.driver.find_element_by_id("url_to_webpage").send_keys(url)

@when("after we wait for a minute")
@then("after we wait for a minute")
def after_we_wait_for_a_minute(context):
    sleep(60)
    
@when("close our browser")
@then("close our browser")
def close_our_browser(context):
    context.driver.quit()

@then("we should see a map")
def we_should_see_a_map(context):
    #assert context.driver.find_element_by_id("map").screenshot_as_base64() == "00"
    #assert context.driver.get_screenshot_as_base64() == "00"
    b64 = context.driver.get_screenshot_as_base64()
    print("b64:", b64[:100])
