Feature: Download
    In order to check to make sure you can download the maps

    Scenario Outline: Download 
        When we start with a link to <url>
         And after we wait for 60 seconds
        Then we should see a map
         And we should be able to download a CSV
         And we should be able to download a GeoJSON
         And we should be able to download a Shapefile

        Examples: urls
            | url |
            | http://edition.cnn.com/2016/06/20/americas/rio-de-janeiro-hospital-attack/index.html |
