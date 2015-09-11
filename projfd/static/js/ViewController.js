app.controller('ViewController', ['$scope', '$http', '$window', '$compile', '$element', function($scope, $http, $window, $compile, $element) {


    $scope.activate = function(){
        var map = L.map('map').setView([51.505, -0.09], 13);

        // add OSM base layer
        var osmLayer = L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors.',
            maxZoom: 18
        }).addTo(map);

        // add data from respective geojson file to changesetsLayer
        $.getJSON( "{{hash}}/geojson.geojson", function( data ) {changesetsLayer.addData(data);});
    };
    $scope.activate();
/*
    $http
    .get('/upload').
    then(function(response) {

    });
*/
}]);

