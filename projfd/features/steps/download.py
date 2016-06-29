from appfd.models import Place
from os.path import isfile
from os import remove
from urllib import urlretrieve


@then('we should be able to download a CSV')
def download_csv(context):
    # not really clicking it to download it... what real testing would be
    # just getting href from link and trying to download that
    # or maybe check wherever Firefoxe's download directory is

    # 1. find button that says csv under download heading
    # 2. click it
    # 3. assert/check if file in Firefox's download directory wherever that is
    # 4. delete file, cleaning up

    #url = context.driver.find_element_by_id("href_csv").get_attribute("href")
    #print("url of csv:", url)
    #path_to_file = "/tmp/test.csv")
    #urlretrieve(url, "/tmp/test.csv")
    #assert isfile("/tmp/test.csv")
    #context.driver.document.getElementById("href_csv").click()
    context.driver.save_screenshot("/tmp/precsv.png")
    context.driver.find_element_by_partial_link_text('CSV').click()
    #path_to_file = "/tmp/"


@then('we should be able to download a GeoJSON')
def download_geojson(context):
    context.driver.find_element_by_partial_link_text('GeoJSON').click()
    #url = context.driver.find_element_by_id("href_geojson").get_attribute("href")
    #print("url of GeoJSON:", url)
    #urlretrieve(url, "/tmp/test.geojson")
    #assert isfile("/tmp/test.geojson")


@then('we should be able to download a Shapefile')
def download_shp(context):
    context.driver.find_element_by_partial_link_text('Shapefile').click()
    #url = context.driver.find_element_by_id("href_shp").get_attribute("href")
    #print("url of Shapefile:", url)
    #urlretrieve(url, "/tmp/test.zip")
    #assert isfile("/tmp/test.zip")
