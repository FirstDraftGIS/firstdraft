app.controller('ViewController', ['$scope', '$http', '$window', '$compile', '$element', '$interval', function($scope, $http, $window, $compile, $element, $interval) {
    console.log("starting ViewController");

    $scope.flipCoordinates = function(obj){
        console.log('statrintg filpcoords with', obj);
        console.log('statrintg filpcoords with', obj.features);
        for (var f = 0; f < obj.features.length; f++)
        {
            var feature = obj.features[f];
            var x = feature.geometry.coordinates[0];
            var y = feature.geometry.coordinates[1];
            obj.features[f].geometry.coordinates[1] = x;
            obj.features[f].geometry.coordinates[0] = y;
        } 
        return obj;
    };


    $scope.activate = function(){
        $scope.loading_map = true;
        map = L.map('map');
        map.setView([0,0],1);

        // add OSM base layer
        var osmLayer = L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors.',
            maxZoom: 18
        }).addTo(map);

        //L.tileLayer.provider('Stamen.Watercolor').addTo(map);
        //var osmLayer = new L.TileLayer.OpenStreetMap();
        //osmLayer.addTo(map);

        // creates style for mainLayer and then creates mainLayer
        var mainLayerStyle = {
            "color": "#ff0000",
            "weight": .5,
            "opacity": .5,
	    "fillOpacity": 0
        };

        function onEachFeature(feature, layer)
        {
            try{
            properties = feature.properties;
            console.log("properties are", properties);
            var popup_html = "<div style='max-height: 250px; overflow-y: auto;'>";
            popup_html += "<h3>" + (properties.name || properties.location);
            if (properties.date_pretty) popup_html += " (" + properties.date_pretty + ")";
            popup_html += "</h3>";
            if(properties['confidence']) popup_html += "<b>confidence: </b>" + properties.confidence + "</br>";
            if(properties['admin_level']) popup_html += "<b>admin level: </b>" + properties.admin_level + "</br>";
            if(properties['pcode']) popup_html += "<b>pcode: </b>" + properties.pcode + "</br>";
            if(properties['geonameid']) popup_html += "<b>geonameid: </b>" + properties.geonameid + "</br>";
            if(properties['context']) popup_html += "<p><b>context: </b>" + properties.context + "</p>";
            popup_html += "</div>";
            console.log("popup_html is", popup_html.substring(0,100));
            layer.bindPopup(popup_html);
            }catch(err){console.error("err is", err);}
        }
        console.log("onEachFeature is", onEachFeature);

        var mainLayer = L.geoJson(undefined,{onEachFeature:onEachFeature, style:mainLayerStyle});
        var featureGroup = L.featureGroup([mainLayer]);
        featureGroup.addTo(map);

       //var sliderControl = L.control.sliderControl({position: "topright", layer: mainLayer});
       //map.addControl(sliderControl);


        map.setView([0,0],1);
 

        $scope.stop = function(){$interval.cancel(promise);};

        var number_of_attempts_to_get_map = 0;
        var promise = $interval( function(){
            number_of_attempts_to_get_map++;
            if (number_of_attempts_to_get_map > 100)
            {
                $scope.stop();
            }
            else
            {
                $http.get('/get_map/' + $scope.$parent.job + '/geojson').then(function(response) {
                    console.log("got map", response);
                    if (response.data)
                    {
                        $scope.stop();
                        mainLayer.addData(response.data);
                        //map.fitBounds(featureGroup.getBounds());
                        console.log('mainLayer is', mainLayer);
                        //console.log('featureGroup is', featureGroup.getBounds());
                        $scope.$parent.show_downloads = true;
                        map.setView([0,0],1);
                        $scope.show_map = true;
                        $scope.loading_map = false;
                        setTimeout(function(){
                            map.invalidateSize();
                            window.scrollTo(0,400);
                            //sliderControl.startSlider();
                        },100);
                    }
                });
            }
        }, 2000);

    };

    $scope.$on('uploaded', function(event, args){
        console.log("uploaded!, so activate");
        $scope.activate();
        //any other action can be perfomed here
    });
}]);

