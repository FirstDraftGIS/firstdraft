from appfd.models import Place
from os.path import isfile
from os import remove
from time import sleep
from urllib import urlretrieve

def download(driver, extension):
    url = driver.find_element_by_id("download_link_" + extension).get_attribute("href")
    path_to_downloaded = "/tmp/test." + extension
    urlretrieve(url, path_to_downloaded)
    assert isfile(path_to_downloaded)

@then("we click download")
def click_download(context):
    context.driver.save_screenshot("/tmp/asdf.png")
    context.driver.find_element_by_css_selector("[data-target='#downloadModal']").click()
    sleep(1)

@then('we should be able to download a CSV')
def download_csv(context):
    download(context.driver, "csv")

@then('we should be able to download a GeoJSON')
def download_geojson(context):
    download(context.driver, "geojson")

@then('we should be able to download a Shapefile')
def download_shp(context):
    download(context.driver, "shp")
