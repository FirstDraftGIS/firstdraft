//collect modals
modals = {};
["start", "paste", "uploadFile", "linkFile", "linkWebpage", "download", "help", "fix", "load"].forEach(function(id) {
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

function hideTable() {
    $(".container").removeClass("split");
    var element = document.getElementById("toggleTableButton")
    element.textContent = "Show Table";
    element.onclick = showTable;
}

function showTable() {
    $(".container").addClass("split");
    var element = document.getElementById("toggleTableButton");
    element.textContent = "Hide Table";
    element.onclick = hideTable;
}

app.controller('MegaController', ['$scope', '$http', '$window', '$compile', '$element', '$interval', function($scope, $http, $window, $compile, $element, $interval) {

  try {

    console.log("$scope.share_url_element:", $scope.share_url_element);

    console.log("starting MegaController");


    $scope.show_advanced_options = false;

    $scope.patterns = {
        //csv: "[^;].*"
        csv: "\d+"
    };


    $scope.closeModal = function(id) {
        modals[id].modal('hide');
    };

    $scope.openModal = function(id) {
        console.log("starting openModal with", id);
        modals.start.modal('hide');
        modals[id].modal('show');
        $(".navbar-collapse").collapse('hide');
    };


    $scope.push_polygons_back = function() {
        _.values(map._layers).filter(function(layer){
            if (layer && layer._latlngs) {
                layer.bringToBack();
            }
        });
    }


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
        $scope.openModal("load");
        var data = {
            'max_time': $scope.max_time,
            'text': $scope.start_text
        };
        if($scope.countries) data.countries = $scope.countries.split(",").map(function(c){return c.trim();});
        $http.post('/request_map_from_text', data).then(function(response) {
            console.log("response is", response);
            $scope.job = response.data;
            $scope.process_job();
            $scope.get_features_when_ready();
        });
        $scope.start_text = "";
        $scope.clear_everything();
        modals.paste.modal('hide');
        //requestFullScreen();
    };

    $scope.request_map_from_file = function() {
        $scope.openModal("load");
        // thx https://uncorkedstudios.com/blog/multipartformdata-file-upload-with-angularjs
        var fd = new FormData();
        fd.append('file', $scope.start_file);
        fd.append('max_time', $scope.max_time);
        if($scope.countries) fd.append("countries", $scope.countries.split(",").map(function(c){return c.trim();}));
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
        //requestFullScreen();
    };

    $scope.request_map_from_urls_to_webpages = function() {
        console.log("starting request_map_from_urls_to_webpages");
        $scope.openModal("load");
        var data = {
            'max_time': $scope.max_time,
            'urls': $scope.urls_to_webpages.split("\n").filter(Boolean)
        };
        if($scope.countries) data.countries = $scope.countries.split(",").map(function(c){return c.trim();});
        $http.post('/request_map_from_urls_to_webpages', data).then(function(response) {
            console.log("Response is", response);
            $scope.job = response.data;
            $scope.process_job();
            $scope.get_features_when_ready();
        });
        $scope.clear_everything();
        modals.linkWebpage.modal('hide');
        //requestFullScreen();
    };

    $scope.request_map_from_urls_to_files = function() {
        console.log("starting request_map_from_urls_to_files");
        $scope.openModal("load");
        var data = {
            'max_time': $scope.max_time,
            'urls': $scope.urls_to_files.split("\n").filter(Boolean)
        };
        if($scope.countries) data.countries = $scope.countries.split(",").map(function(c){return c.trim();});
        $http.post('/request_map_from_urls_to_files', data).then(function(response) {
            console.log("Response is", response);
            $scope.job = response.data;
            $scope.process_job();
            $scope.get_features_when_ready();
        });
        $scope.clear_everything();
        modals.linkFile.modal('hide');
        //requestFullScreen();
    };

    $scope.features = [];
    $scope.correct_features = [];
    $scope.features_that_appear_in_table = [];
    $scope.downloadModal = $(document.getElementById("downloadModal"));
    $scope.editModal = $(document.getElementById("editModal"));
    $scope.fixModal = $(document.getElementById("fixModal"));
    $scope.loadModal = $(document.getElementById("loadModal"));
    $scope.max_time = 10;
    //$('#download_link_csv').href = '/get_map/' + job + '/csv';
    //$('#download_link_geojson').href = '/get_map/' + job + '/geojson';
    //$('#download_link_shp').href = '/get_map/' + job + '/zip';

    map = L.map('map', {"fullscreenControl": true});

    var showTableControl = L.Control.extend({
        options: {
            position: "topright",
        },
        onAdd: function(map) {
            var showTableButton = L.DomUtil.create("div", "leaflet-bar leaflet-control leaflet-control-custom");
            showTableButton.style.boxShadow = 'none';
            showTableButton.id = "showTableControl";
            showTableButton.innerHTML = "<div style='border: none; box-shadow: none; padding: 5px'><button type='button' id='toggleTableButton' class='btn btn-primary btn-xs' onclick='showTable()'>Show Table</button></div>";
            return showTableButton;
        }
    });
    map.addControl(new showTableControl());

    centerControl = $("<div class='leaflet-top leaflet-center' style='display: none'><div class='leaflet-control leaflet-control-custom'><div id='map-alert' class='alert alert-warning fade in' style='padding-bottom: 5px; padding-top: 5px;'></div></div></div>");
    map._controlContainer.appendChild(centerControl[0]);

    map.setView([0,0],2);
    L.tileLayer(location.protocol + '//{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data &copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors.',
        maxZoom: 18
    }).addTo(map);


    $scope.clear_layers = function() {
        map.eachLayer(function(layer) {
            if(!layer._url) { // skipping over basemaps
                map.removeLayer(layer);
            }
        });
    };

    $scope.clear_everything = function() {
        console.log("starting clear_everything");
        $scope.clear_layers();
        $scope.correct_features = [];
        $scope.countries = "";
        $scope.features = [];
        $scope.features_that_appear_in_table = [];
        $scope.show_advanced_options = false;
        $scope.start_file = null;
        $scope.start_text = "";
        $scope.urls_to_files = "";
        $scope.urls_to_webpages = "";
    };


    function getStyle(feature) {
        //if (feature.confidence === 1) color = "green";
        //if (feature.confidence > .9) color = "yellow";
        //color = "red";
        color = "purple";
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


    $scope.fixLocationUsingTheMap = fixLocation = function(feature) {

        console.log("starting fixLocation with feature id of ", feature);

        document.getElementById("map-alert").textContent = "Fixing " + feature.name;
        centerControl.show();

        $scope.mode = "fixing";

        $scope.fixModal.modal("hide");

        var name = feature.name;

        var options = $scope.features.filter(function(feature) {
            return feature.name === name;
        });

        console.log("OPTIONS:", options);

        // hide all the other locations
        $scope.features_that_appear_in_table = options;

        // clear map
        $scope.clear_layers();


        function onmouseover(event) {
            event.target.setStyle({color: "#00FF00", fillColor: "#00FF00"});
        }

        function onmouseout(event) {
            event.target.setStyle({color: "purple", fillColor: "purple"});
        }

        function onclick(feature) {
            return function (event) {
                console.log("starting onclick", event, feature);
                if ($scope.selection.featureplace_id != feature.featureplace_id) {
                    var url = window.location.origin + "/api/change_featureplace";
                    $http.post(url, {featureplace_id: $scope.selection.featureplace_id, correct: false});
                    $http.post(url, {featureplace_id: feature.featureplace_id, correct: true});
                    _.find($scope.features, function(f) { return f.featureplace_id === $scope.selection.featureplace_id; }).correct = false;
                    feature.correct = true;
                }
                centerControl.hide();
                map.removeLayer($scope.featureGroup);
                $scope.loadFeatures();
            };
        };

        $scope.featureGroup = new L.featureGroup();
        // show all the incorrect locations
        options.forEach(function(feature) {

            var marker = L.circleMarker([feature.latitude, feature.longitude], getStyle(feature));
            marker.on("click", onclick(feature));
            marker.on("mouseover", onmouseover);
            marker.on("mouseout", onmouseout);
            $scope.featureGroup.addLayer(marker);

            if (feature.polygon) {
                var polygon = L.polygon(turf.flip(turf.polygon(feature.polygon)).geometry.coordinates, getStyle(feature)).addTo(map);
                polygon.on("click", onclick(feature));
                polygon.on("mouseover", onmouseover);
                polygon.on("mouseout", onmouseout);
                $scope.featureGroup.addLayer(polygon);
            }

            if (feature.multipolygon) {
                var multipolygon = L.polygon(turf.flip(turf.multiPolygon(feature.multipolygon)).geometry.coordinates, getStyle(feature)).addTo(map);
                multipolygon.on("click", onclick(feature));
                multipolygon.on("mouseover", onmouseover);
                multipolygon.on("mouseover", onmouseout);
                $scope.featureGroup.addLayer(multipolygon);
            }
        });

        $scope.featureGroup.addTo(map);
        map.fitBounds($scope.featureGroup.getBounds());
        $scope.push_polygons_back();

    };

    $scope.numberToString = function(n) {
        return _.last(String(n).split(".")).length > 4 ? n.toFixed(4) + "..." : n.toFixed(4);
    };

    $scope.loadFeatures = function() {
    
        $scope.correct_features = $scope.features.filter(function(feature){return feature.correct;});
        $scope.correct_features.forEach(function(feature) {

            var popup_html = "<div style='text-align:center'><b>"+feature.name+"</b></div>" +
                "<div><b>Latitude:</b> " + $scope.numberToString(feature.latitude) + "</div>" +
                "<div><b>Longitude:</b> " + $scope.numberToString(feature.longitude) + "</div>" +
                "<div style='text-align: center'><button type='button' class='btn btn-warning btn-xs' onclick='displayFixModalById(" + feature.featureplace_id + ")' style='margin: 5px;'>Fix Location</button></div>" +
                "<button type='button' class='btn btn-primary btn-xs' onclick='displayEditModalById(" + feature.featureplace_id + ")' style='margin: 5px;'>More</button>" +
                "<button type='button' class='btn btn-danger btn-xs pull-right' onclick='deleteByFeaturePlaceIdFromPopup(" + feature.featureplace_id + ")' style='margin: 5px;'>Delete</button>";

            var popup_options = {
                'maxWidth': '500',
                'className' : 'custom-popup'
            };
                
            var marker = L.circleMarker([feature.latitude, feature.longitude], getStyle(feature));
            marker.feature_id = feature.feature_id;
            marker.featureplace_id = feature.featureplace_id;
            marker.bindPopup(popup_html, popup_options);
            marker.addTo(map);

            if (feature.polygon) {
                console.log("creating polygon for", feature);
                var polygon = L.polygon(turf.flip(turf.polygon(feature.polygon)).geometry.coordinates, getStyle(feature)).addTo(map);
                polygon.feature_id = feature.feature_id;
                polygon.featureplace_id = feature.featureplace_id;
                polygon.bindPopup(popup_html, popup_options);
                polygon.addTo(map);
                console.log("pushed", polygon);
            }

            if (feature.multipolygon) {
                console.log("creating multipolygon for", feature);
                var multipolygon = L.polygon(turf.flip(turf.multiPolygon(feature.multipolygon)).geometry.coordinates, getStyle(feature)).addTo(map);
                multipolygon.feature_id = feature.feature_id;
                multipolygon.featureplace_id = feature.featureplace_id;
                multipolygon.bindPopup(popup_html, popup_options);
                multipolygon.addTo(map);
                console.log("pushed", multipolygon);
            }
        });
        $scope.push_polygons_back();
        $scope.features_that_appear_in_table = $scope.correct_features;
        $scope.loadModal.modal("hide");
    };

    $scope.getFeatures = function() {
        console.log("starting getFeatures");
        $http.get(window.location.origin + "/api/features/" + $scope.job).then(function(response) {
            console.log("response:", response);
            $scope.features = response.data.features;
            $scope.loadFeatures();
        });
    };

    $scope.deleteSelection = function() {
        console.log("starting delete selection with", $scope.selection);
        var featureplace_id = $scope.selection.featureplace_id;
        $scope.deleteByFeaturePlaceId(featureplace_id);
    };

    $scope.deleteByFeaturePlaceId = deleteByFeaturePlaceId = function(featureplace_id) {
        console.log("starting deleteByFeaturePlaceId with", featureplace_id);
        $http.post(window.location.origin + "/api/change_featureplace", {featureplace_id: featureplace_id, correct: false}).then(function(response) {
            console.log("response to change_featureplace is", response);
        });

        _.find($scope.features, function(f) { return f.featureplace_id === featureplace_id; }).correct = false;

        $scope.correct_features = $scope.features.filter(function(feature){return feature.correct;});

        //not sure if this is necessary
        $scope.gridApi.core.refresh();

        // find in map and delete 
        map.eachLayer(function(layer) {
            if (layer.featureplace_id === featureplace_id) {
                map.removeLayer(layer);
            }
        });
        $scope.features_that_appear_in_table = $scope.correct_features;
        $scope.editModal.modal("hide");
        $scope.selection = {};
    };

    $scope.deleteByFeaturePlaceIdFromPopup = deleteByFeaturePlaceIdFromPopup = function(featureplace_id) {
        $scope.$apply(function() {
            $scope.deleteByFeaturePlaceId(featureplace_id);
        });
    }

    $scope.displayEditModal = displayEditModal= function(entity) {
        console.log("entity:", entity);
        close_all_modals();
        if (entity) $scope.selection = entity;
        $scope.editModal.modal();
    };

    $scope.displayEditModalById = displayEditModalById = function(featureplace_id) {
        console.log("featureplace_id:", featureplace_id);
        $scope.$apply(function(){
            $scope.selection = _.find($scope.features, function(feature) { return feature.featureplace_id === featureplace_id; });
        });
        console.log("selection:", $scope.selection);
        $scope.editModal.modal();
    };

    $scope.displayFixModalById = displayFixModalById = function(featureplace_id) {
        console.log("featureplace_id:", featureplace_id);
        $scope.$apply(function(){
            $scope.selection = _.find($scope.features, function(feature) { return feature.featureplace_id === featureplace_id; });
        });
        console.log("selection:", $scope.selection);
        $scope.fixModal.modal();
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


    columnDefs = [
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
        {displayName: 'Name', enableFiltering: true, enableSorting: true, field: 'name'}
        //{displayName: 'Confidence', enableCellEdit: false, enableFiltering: true, enableSorting: true, field: 'confidence'},
    ];
    if (window.innerWidth > 600) {
        columnDefs.push({displayName: 'Geom. Used', enableCellEdit: true, enableCellEditOnFocus: true, editableCellTemplate: 'ui-grid/dropdownEditor', editDropdownOptionsFunction: $scope.editDropdownOptionsFunction, enableFiltering: true, enableSorting: true, field: 'geometry_used'});
    } else {
        columnDefs.push({displayName: 'Geom. Used', enableCellEdit: true, enableCellEditOnFocus: true, editableCellTemplate: 'ui-grid/dropdownEditor', editDropdownOptionsFunction: $scope.editDropdownOptionsFunction, enableFiltering: true, enableSorting: true, field: 'geometry_used', visible: false});
    }
 


    $scope.gridOptions = {
        columnDefs: columnDefs,
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
