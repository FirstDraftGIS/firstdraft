app.controller('ViewController', ['$scope', '$http', '$window', '$compile', '$element', '$interval', function($scope, $http, $window, $compile, $element, $interval) {

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
            try
            {
                layer.bindPopup(feature.properties.name);
            }
            catch(err){console.log("err is", err);}
        }

        var mainLayer = L.geoJson(undefined,{onEachFeature:onEachFeature, style:mainLayerStyle});
        var featureGroup = L.featureGroup([mainLayer]);
        featureGroup.addTo(map);
        map.setView([0,0],1);
 

        $scope.stop = function(){$interval.cancel(promise);};

        var promise = $interval( function(){
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
                    setTimeout(function(){
                        map.invalidateSize();
                        window.scrollTo(0,400);
                    },100);
                }
            });
        }, 2000);

    };

    $scope.$on('uploaded', function(event, args){
        console.log("uploaded!, so activate");
        $scope.activate();
        //any other action can be perfomed here
    });
}]);

