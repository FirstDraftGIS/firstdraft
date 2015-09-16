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
        var map = L.map('map').setView([51.505, -0.09], 13);

        // add OSM base layer
        var osmLayer = L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors.',
            maxZoom: 18
        }).addTo(map);

        // creates style for changesetsLayer and then creates changesetsLayer
        var mainLayerStyle = {
            "color": "#ff0000",
            "weight": .5,
            "opacity": .5,
	    "fillOpacity": 0
        };
        var mainLayer = L.geoJson(undefined,{style:mainLayerStyle}).addTo(map);

        // add data from respective geojson file to changesetsLayer
        //$.getJSON( $scope.$parent.job + "/job" + .geojson, function( data ) {changesetsLayer.addData(data);});

        $scope.stop = function(){$interval.cancel(promise);};

        var promise = $interval( function(){
            $http.get('/get_map/' + $scope.$parent.job + '/geojson').then(function(response) {
                console.log("got map", response);
                if (response.data)
                {
                    $scope.stop();
                    mainLayer.addData(response.data);
                    var featureGroup = L.featureGroup([mainLayer]);
                    map.fitBounds(featureGroup.getBounds());
                    console.log('mainLayer is', mainLayer);
                    console.log('featureGroup is', featureGroup.getBounds());
                    $scope.$parent.show_downloads = true;
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

