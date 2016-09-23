//collect modals
modals = {};
["start", "paste", "uploadFile", "linkFile", "linkWebpage", "download", "help"].forEach(function(id) {
    modals[id] = $("#" + id + "Modal");
});

function close_all_modals () {
    for (var modal in modals) {
       modals[modal].modal('hide');
    }
}

// has to be initiated by a user gesture
// which means I should place this in a button
function requestFullScreen() {
    var html = document.documentElement;
    if (html.requestFullscreen) html.requestFullscreen();
    if (html.webkitRequestFullscreen) html.webkitRequestFullscreen();
    if (html.mozRequestFullScreen) html.mozRequestFullScreen();
    if (html.msRequestFullscreen) html.msRequestFullscreen();
}


share_url_element = document.getElementById("share_url");

app.controller('MegaController', ['$scope', '$http', '$window', '$compile', '$element', '$interval', function($scope, $http, $window, $compile, $element, $interval) {

  try {

    console.log("$scope.share_url_element:", $scope.share_url_element);

    console.log("starting MegaController");


    $scope.openModal = function(id) {
        console.log("starting openModal with", id);
        modals.start.modal('hide');
        modals[id].modal('show');
    };

    $scope.process_job = function() {
        console.log("starting process_job with $scope.share_url_element:", $scope.share_url_element);
        window.location.hash = $scope.job;
        $scope.share_url = window.location.origin + "/view_map/" + $scope.job;
        console.log("scope.share-Url:", $scope.share_url);
        share_url_element.href = $scope.share_url;
        share_url_element.textContent = $scope.share_url;
        $scope.check_downloadability_of_extension("csv");
        $scope.check_downloadability_of_extension("geojson");
        $scope.check_downloadability_of_extension("shp");
    };

    $scope.start_text = "";
    $scope.request_map_from_text = function() {
        $http.post('/request_map_from_text', {'text': $scope.start_text}).then(function(response) {
            console.log("response is", response);
            $scope.job = response.data;
            $scope.process_job();
            $scope.get_features_when_ready();
        });
        $scope.start_text = "";
        $scope.clear_everything();
        modals.paste.modal('hide');
        requestFullScreen();
    };

    $scope.request_map_from_file = function() {
        // thx https://uncorkedstudios.com/blog/multipartformdata-file-upload-with-angularjs
        var fd = new FormData();
        fd.append('file', $scope.start_file);
        $http.post('/request_map_from_file', fd, {
            transformRequest: angular.identity,
            headers: {'Content-Type': undefined}
        }).then(function(response) {
            $scope.job = response.data;
            $scope.process_job();
            $scope.get_features_when_ready();
        }); 
        $scope.clear_everything();
        $scope.clear_everything();
        modals.uploadFile.modal('hide');
        requestFullScreen();
    };

    $scope.request_map_from_urls_to_webpages = function() {
        console.log("starting request_map_from_urls_to_webpages");
        $http.post('/request_map_from_urls_to_webpages', {'urls': $scope.urls_to_webpages.split("\n").filter(Boolean)}).then(function(response) {
            console.log("Response is", response);
            $scope.job = response.data;
            $scope.process_job();
            $scope.get_features_when_ready();
        });
        $scope.clear_everything();
        modals.linkWebpage.modal('hide');
        requestFullScreen();
    };

    $scope.request_map_from_urls_to_files = function() {
        console.log("starting request_map_from_urls_to_files");
        $http.post('/request_map_from_urls_to_files', {'urls': $scope.urls_to_files.split("\n").filter(Boolean)}).then(function(response) {
            console.log("Response is", response);
            $scope.job = response.data;
            $scope.process_job();
            $scope.get_features_when_ready();
        });
        $scope.clear_everything();
        modals.linkFile.modal('hide');
        requestFullScreen();
    };

    $scope.layers = [];
    $scope.features = [];
    $scope.features_that_appear_in_table = [];
    $scope.editModal = $(document.getElementById("editModal"));
    $scope.downloadModal = $(document.getElementById("downloadModal"));
    //$('#download_link_csv').href = '/get_map/' + job + '/csv';
    //$('#download_link_geojson').href = '/get_map/' + job + '/geojson';
    //$('#download_link_shp').href = '/get_map/' + job + '/zip';

    map = L.map('map', {"fullscreenControl": true});
    map.setView([0,0],2);
    L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors.',
        maxZoom: 18
    }).addTo(map);


    $scope.clear_everything = function() {
        console.log("starting clear_everything");
        $scope.start_text = "";
        $scope.start_file = null;
        $scope.urls_to_files = "";
        $scope.urls_to_webpages = "";
        $scope.layers.forEach(function(layer) {
            map.removeLayer(layer);
        });
        $scope.layers = [];
        $scope.features = [];
        $scope.features_that_appear_in_table = [];
    };


    function getStyle(feature) {
        if (feature.confidence === 1) color = "green";
        if (feature.confidence > .9) color = "yellow";
        color = "red";
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

    $scope.get_features_when_ready = function() {
        console.log("starting get_features_when_ready");
        

        function stop() { $interval.cancel(request);};

        var request = $interval( function(){
            console.log("checking if", $scope.job, "is ready"); 
            $http.get('/api/ready/' + $scope.job).then(function(response) {
                console.log("got response", response);
                if (response.data === "ready") {
                    stop();
                    $scope.getFeatures();
                }
            });
        }, 2000);

    };

    $scope.check_downloadability_of_extension = function(extension) {
        function stop() { $interval.cancel(request); };

        var request = $interval( function(){
            console.log("checking if", $scope.job, extension, "is ready");
            document.getElementById("download_link_" + extension).href = window.location.origin + "/get_map/" + $scope.job + "/" + extension;
            $http.get('/does_map_exist/' + $scope.job + "/" + extension).then(function(response) {
                console.log("got response", response);
                if (response.data === "yes") {
                    stop();
                    $scope["ready_to_download_" + extension] = true;
                } else {
                    $scope["ready_to_download_" + extension] = false;
                }
            });
        }, 2000);
    }; 

    $scope.getFeatures = function() {
      console.log("starting getFeatures");
      $http.get(window.location.origin + "/api/features/" + $scope.job).then(function(response) {
        console.log("response:", response);
        $scope.features = response.data.features;
        // include correct = null in table.  correct=null means idk if it's correct or not
        $scope.features_that_appear_in_table = $scope.features.filter(function(feature){return feature.correct != false;});
        $scope.features.forEach(function(feature) {

            var popup_html = "<div style='text-align:center'><b>"+feature.name+"</b></div>" +
                "<div><b>Latitude:</b> " + feature.latitude + "</div>" +
                "<div><b>Longitude:</b> " + feature.longitude + "</div>" +
                "<button type='button' class='btn btn-primary btn-xs' onclick='displayEditModalById(" + feature.id + ")' style='margin: 5px;'>More</button>" +
                "<button type='button' class='btn btn-danger btn-xs pull-right' onclick='deleteByFeatureIdFromPopup(" + feature.id + ")' style='margin: 5px;'>Delete</button>";

            var popup_options = {
                'maxWidth': '500',
                'className' : 'custom-popup'
            };
                
            var marker = L.circleMarker([feature.latitude, feature.longitude], getStyle(feature));
            marker.feature_id = feature.id;
            marker.bindPopup(popup_html, popup_options);
            if (feature.correct != false) marker.addTo(map);
            $scope.layers.push(marker);

            if (feature.polygon) {
                console.log("creating polygon for", feature);
                var polygon = L.polygon(turf.flip(turf.polygon(feature.polygon)).geometry.coordinates, getStyle(feature)).addTo(map);
                polygon.feature_id = feature.id;
                polygon.bindPopup(popup_html, popup_options);
                if (feature.correct != false) polygon.addTo(map);
                $scope.layers.push(polygon);
                console.log("pushed", polygon);
            }

            if (feature.multipolygon) {
                console.log("creating multipolygon for", feature);
                var multipolygon = L.polygon(turf.flip(turf.multiPolygon(feature.multipolygon)).geometry.coordinates, getStyle(feature)).addTo(map);
                multipolygon.feature_id = feature.id;
                multipolygon.bindPopup(popup_html, popup_options);
                if (feature.correct != false) multipolygon.addTo(map);
                $scope.layers.push(multipolygon);
                console.log("pushed", multipolygon);
            }
        });
    });


    };

    $scope.changeText = function() {
        $http.post(window.location.origin + "/api/change_feature/" + feature_id, json={"text": $scope.selection.text}).then(function(response) {
            console.log("response:", response);
        });
    };

    $scope.deleteSelection = function() {
        console.log("starting delete selection with", $scope.selection);
        var feature_id = $scope.selection.id;
        $scope.deleteByFeatureId(featured_id);
    };

    $scope.deleteByFeatureId = deleteByFeatureId = function(feature_id) {
        console.log("starting deleteByFeatureId with", feature_id);
        $http.get(window.location.origin + "/api/delete_feature/" + feature_id).then(function(response) {
            console.log("response:", response);
        });
        // find in rows and delete
        $scope.features_that_appear_in_table = $scope.features_that_appear_in_table.filter(function(feature) {
            return feature.id != feature_id;
        });

        //not sure if this is necessary
        $scope.gridApi.core.refresh();

        // find in map and delete 
        for (var key in map._layers) {
            var layer = map._layers[key];
            if (layer.feature_id === feature_id) {
                map.removeLayer(layer);
            }
        }
        $scope.editModal.modal("hide");
        $scope.selection = {};
    };

    $scope.deleteByFeatureIdFromPopup = deleteByFeatureIdFromPopup = function(feature_id) {
        $scope.$apply(function() {
            $scope.deleteByFeatureId(feature_id);
        });
    }

    $scope.displayEditModal = displayEditModal= function(entity) {
        console.log("entity:", entity);
        $scope.selection = entity;
        $scope.editModal.modal();
    };

    $scope.displayEditModalById = displayEditModalById = function(feature_id) {
        console.log("feature_id:", feature_id);
        $scope.$apply(function(){
            $scope.selection = _.find($scope.features, function(feature) { return feature.id === feature_id; });
        });
        console.log("selection:", $scope.selection);
        $scope.editModal.modal();
    };



    $scope.editDropdownOptionsFunction = function(rowEntity, columnDef) {
        console.log("starting scope.editDropdownOptionsFunction with", rowEntity, columnDef);
        if (!rowEntity.geometries) {
            rowEntity.geometries = [];
            if (rowEntity.latitude && rowEntity.longitude) { rowEntity.geometries.push({id: "Point", value: "point"});}
            if (rowEntity.line) { rowEntity.geometries.push({id: "Line", value: "line"});}
            if (rowEntity.polygon) { rowEntity.geometries.push({id: "Polygon", value: "polygon"});}
            if (rowEntity.multipolygon) { rowEntity.geometries.push({id: "MultiPolygon", value: "multipolygon"});}
        }
        return rowEntity.geometries;
    };

    $scope.gridOptions = {
        columnDefs: [
            {
                cellTemplate: '<div style="padding: 2px;"><span class="glyphicon glyphicon-new-window popup" aria-hidden="true" ng-click="grid.appScope.displayEditModal(row.entity)"></span></div>',
                displayName: ' ',
                enableHiding: false,
                enableFiltering: false,
                enableSorting: false,
                hideHeader: true,
                filterHeaderTemplate: "<div></div>",
                field: 'id',
                width: 25
            },
            {displayName: 'Name', enableFiltering: true, enableSorting: true, field: 'name'},
            {displayName: 'Confidence', enableCellEdit: false, enableFiltering: true, enableSorting: true, field: 'confidence'},
            {displayName: 'Geom. Used', enableCellEdit: true, enableCellEditOnFocus: true, editableCellTemplate: 'ui-grid/dropdownEditor', editDropdownOptionsFunction: $scope.editDropdownOptionsFunction, enableFiltering: true, enableSorting: true, field: 'geometry_used'}
        ],
        data: "features_that_appear_in_table",
        enableFiltering: true,
        enablePaginationControls: false,
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
        rowTemplate: '<div ng-right-click="showRowMenu()">' +
                ' <div ng-repeat="(colRenderIndex, col) in colContainer.renderedColumns track by col.colDef.name" class="ui-grid-cell" ng-class="{ \'ui-grid-row-header-cell\': col.isRowHeader }"  ui-grid-cell></div>' +
              '</div>',
        showFilter: true,
        showSelectionBox: true
    };

    $scope.showRowMenu = function() {
        console.log("showRowMenu:");
    };

    $scope.undo = function() {
        document.execCommand("undo", "", null);
    };

    $scope.$watch('selection', function(newValue, oldValue) {
        console.log("newValue:", newValue, "oldValue:", oldValue);
    });


    console.log("finishing MegaController");

    if (window.location.hash) {
        $scope.job = window.location.hash.replace("#","");
        $scope.process_job();
        $scope.get_features_when_ready();
    } else {
        modals.start.modal();
    }

  } catch (err) { console.error(err); }

}]);
