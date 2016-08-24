app.controller('MegaController', ['$scope', '$http', '$window', '$compile', '$element', '$interval', function($scope, $http, $window, $compile, $element, $interval) {

  try {

    console.log("starting MegaController");

    $scope.layers = [];
    $scope.features = [];

    downloadModal = $(document.getElementById("downloadModal"));
    $('#download_link_csv').href = '/get_map/' + job + '/csv';
    $('#download_link_geojson').href = '/get_map/' + job + '/geojson';
    $('#download_link_shp').href = '/get_map/' + job + '/zip';

    map = L.map('map', {"fullscreenControl": true});
    map.setView([0,0],2);
    L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors.',
        maxZoom: 18
    }).addTo(map);

    function getStyle(feature) {
        if (feature.confidence === "high") color = "green";
        if (feature.confidence === "medium") color = "yellow";
        if (feature.confidence === "low") color = "red";
        var options = {
            clickable: true,
            color: color,
            fillColor: color
        };
        return options;
    }

    $scope.setStyleForRowItem = function(rowItem) {
        console.log("starting setStyleForRowItem with", rowItem);
    }

    $http.get(window.location.origin + "/api/features/" + job).then(function(response) {
        console.log("response:", response);
        $scope.features = response.data.features;
        $scope.features.forEach(function(feature) {
            var marker = L.circleMarker([feature.latitude, feature.longitude], getStyle(feature));
            marker.bindPopup(
                "<div style='text-align:center'><b>"+feature.name+"</b></div>" +
                "<div><b>Latitude:</b> " + feature.latitude + "</div>" +
                "<div><b>Longitude:</b> " + feature.longitude + "</div>"
            ).addTo(map);
            $scope.layers.push(marker);

            if (feature.polygon) {
                console.log("creating polygon for", feature);
                var polygon = L.polygon(turf.flip(turf.polygon(feature.polygon)).geometry.coordinates, getStyle(feature)).addTo(map);
                polygon.bindPopup(
                "<div style='text-align:center'><b>"+feature.name+"</b></div>" +
                "<div><b>Latitude:</b> " + feature.latitude + "</div>" +
                "<div><b>Longitude:</b> " + feature.longitude + "</div>"
                ).addTo(map);
                $scope.layers.push(polygon);
                console.log("pushed", polygon);
            }

            if (feature.multipolygon) {
                console.log("creating multipolygon for", feature);
                var multipolygon = L.polygon(turf.flip(turf.multiPolygon(feature.multipolygon)).geometry.coordinates, getStyle(feature)).addTo(map);
                multipolygon.bindPopup(
                "<div style='text-align:center'><b>"+feature.name+"</b></div>" +
                "<div><b>Latitude:</b> " + feature.latitude + "</div>" +
                "<div><b>Longitude:</b> " + feature.longitude + "</div>"
                ).addTo(map);
                $scope.layers.push(multipolygon);
                console.log("pushed", multipolygon);
            }
        });
    });

    $scope.gridOptions = {
        columnDefs: [
            {displayName: 'Name', enableFiltering: true, enableSorting: true, field: 'name'},
            {displayName: 'Confidence', enableFiltering: true, enableSorting: true, field: 'confidence'},
            {displayName: 'Latitude', enableFiltering: true, enableSorting: true, field: 'latitude'},
            {displayName: 'Longitude', enableFiltering: true, enableSorting: true, field: 'longitude'},
        ],
        data: "features",
        enableFiltering: true,
        enablePaging: true,
        enableRowHeaderSelection: true,
        enableRowSelection: true,
        enableSelectAll: true,
        enableSorting: true,
        filterOptions: {
            filterText: ""
        },
        multiSelect: true,
        onRegisterApi: function(api) {
            $scope.gridApi = api;
            api.selection.on.rowSelectionChanged($scope, function(rowItem){
                $scope.setStyleForRowItem(rowItem);
            });
            api.selection.on.rowSelectionChangedBatch($scope, function(rows){
                rows.forEach(function(rowItem){
                    $scope.setStyleForRowItem(rowItem);
                });
            });
        },
        paginationPageSizes: [100],
        paginationPageSize: 100,
        rowTemplate: '<div ng-right-click="showRowMenu()">' +
                ' <div ng-repeat="(colRenderIndex, col) in colContainer.renderedColumns track by col.colDef.name" class="ui-grid-cell" ng-class="{ \'ui-grid-row-header-cell\': col.isRowHeader }"  ui-grid-cell></div>' +
              '</div>',
        showFilter: true,
        showSelectionBox: true
    };

    $scope.showRowMenu = function() {
        console.log("showRowMenu:");
    };


    console.log("finishing MegaController");

  } catch (err) { console.error(err); }

}]);
