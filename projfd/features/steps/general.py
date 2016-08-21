from appfd.models import Place
from django.core.mail import send_mail
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
    context.driver.find_element_by_id("next").click()

@when("user enters a link to a file at {url}")
def start_with_a_link_to_a_file(context, url):
    print("url:", url)
    context.driver.find_element_by_css_selector("input[value=url_to_file]").click()
    context.driver.find_element_by_id("url_to_file").send_keys(url)
    context.driver.find_element_by_id("next").click()

@when("after we wait for {x} seconds")
@then("after we wait for {x} seconds")
def after_we_wait_for_x_number_of_seconds(context, x):
    sleep(float(x))

"""
@when("after we wait up to {x} minutes for the screen to change")
def after_we_wait_up_to_x_minutes_for_screen_to_change(context, x):
    total_seconds_to_wait = x * 60
    start = datetime.now()
    screenshot = context.driver.get_screenshot_as_png()
"""    
    
    
@when("close our browser")
@then("close our browser")
def close_our_browser(context):
    context.driver.quit()

@then("we should see a map after a while")
def we_should_see_a_map_after_a_while(context):
    for x in range(25):
        print("checking size of map")
        sleep(5)
        size = context.driver.find_element_by_id("map").size
        if size['width'] > 100 and size['height'] > 100:
            break
    try:
        assert(size['width'] > 100)
        assert(size['height'] > 100)
    except Exception as e:
        try:
            print("page_source is")
            print(context.driver.page_source.encode("ascii", "ignore"))
            print("html is")
            print(context.driver.execute_script("return document.documentElement.innerHTML;").decode("utf-8").encode("ascii","ignore"))
        except Exception as e1:
            print(e1)
        raise e
 

@then("we should see a map")
def we_should_see_a_map(context):
    # for some reason we're getting an error when we try to get b64/png image
    #assert context.driver.find_element_by_id("map").screenshot_as_base64() == "00"
    #assert context.driver.get_screenshot_as_base64() == "00"
    #b64 = context.driver.get_screenshot_as_base64()
    context.driver.save_screenshot("/tmp/screenshot.png")
    base64 = context.driver.get_screenshot_as_base64()
    size = context.driver.find_element_by_id("map").size
    try:
        assert(size['width'] > 100)
        assert(size['height'] > 100)
    except Exception as e:
        try:
            print("page_source is")
            print(context.driver.page_source.encode("ascii", "ignore"))
            print("html is")
            print(context.driver.execute_script("return document.documentElement.innerHTML;").decode("utf-8").encode("ascii","ignore"))
        except Exception as e1:
            print(e1)
        raise e
        
