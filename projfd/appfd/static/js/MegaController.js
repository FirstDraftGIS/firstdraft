function load_script(path_to_script) {
    return new Promise((resolve, reject) => {
        var script = document.createElement("script");
        document.body.appendChild(script);
        script.onload = function () {
            console.log("loaded " + path_to_script);
            resolve("loaded " + path_to_script);
        };
        script.src = path_to_script;
    });
}

Object.defineProperty(window, "scope", {
    get: function() {
        return angular.element(document.getElementById("map")).scope();
    }
});


Object.defineProperty(window, 'modals', {
    get: function() {
        return Array.prototype.slice.call(document.querySelectorAll(".modal"))
        .reduce((acc, element) => {
            $(element).on("shown.bs.modal", () => $("body").addClass("modal-open"));
            acc[element.id.replace("Modal","")] = $(element);
            return acc;
        }, {});
    }
});

function close_all_modals () {
    $(".modal").modal("hide");
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

app.controller('MegaController', ['$scope', '$http', '$window', '$compile', '$element', '$interval', '$templateRequest', '$sce',  function($scope, $http, $window, $compile, $element, $interval, $templateRequest, $sce) {

  try {

    console.log("$scope.share_url_element:", $scope.share_url_element);

    console.log("starting MegaController");

    $scope.previous_maps = [];
    if (localStorage['settings']) {
        $scope.settings = JSON.parse(localStorage['settings']);
    } else {
        $scope.settings = {}
    }

    $scope.sources = [];
    $scope.show_advanced_options = false;

    $scope.patterns = {
        //csv: "[^;].*"
        csv: "\d+"
    };

    $scope.load_modal = function(id) {
        return new Promise(function(resolve, reject){
             var templateUrl = $sce.getTrustedResourceUrl('static/modals/' + id +'.html');
             console.log("templateUrl:", templateUrl);
             $templateRequest(templateUrl).then(function(template) {
                 console.log("template:", template);
                 var div = document.createElement("div");
                 document.body.appendChild(div);
                 $compile($(div).html(template).contents())($scope);
                 resolve();
             });
        });
    };

    $scope.load_modal_if_necessary = function(id) {
        return new Promise(function(resolve) {
            if (modals[id]) {
                resolve();
            } else {
                resolve($scope.load_modal(id));
            }
        });
    };


    $scope.closeModal = function(id) {
        modals[id].modal('hide');
    };

    navbar_collapse = $(".navbar-collapse");
    $scope.open_modal = function(id) {
        modals[id].modal('show');
        navbar_collapse.collapse('hide');
    };

    $scope.close_all_modals = close_all_modals;

    $scope.close_all_modals_and_open = close_all_modals_and_open = function(id) {
        console.log("starting close_all_modals_and_open with", id);
        close_all_modals();
        $scope.load_modal_if_necessary(id).then(function() {
            $scope.open_modal(id);
        });
    };

    $scope.create_a_map = function() {
        $scope.sources = [];
        $scope.close_all_modals_and_open("sources");
        $scope.clear_everything();
    };

    $scope.getClassForTypeOfSource = function(type) {
        switch(type) {
            case 'file':
                return 'glyphicon-file';
            case 'link':
                return 'glyphicon-link';
            case 'text':
                return 'glyphicon-text-size';
        }
    };


    $("#file-to-add").change(function(event){
        var files = event.target.files;
        if (files.length > 0) {
            var file = event.target.files[0];
        
            $scope.sources.push({
                type: "file",
                data: file,
                name: file.name
            });
            $scope.$apply(); // updates view like contentinit in Angular 2
            $scope.close_all_modals_and_open("sources");
        }
   });


    $scope.add = {
        links: function() {
            console.log("link");
            if ($scope.text_of_links_to_add && $scope.text_of_links_to_add.length > 0) {
                $scope.text_of_links_to_add.split("\n").forEach(function(line) {
                    if (line && line.length > 5) {
                        var link = line.trim();
                        if (!link.startsWith("http")) {
                            link = "http://" + link;
                        }
                        $scope.sources.push({
                            type: "link",
                            data: link
                        });
                    }
                });
                $scope.text_of_links_to_add = "";
                $scope.close_all_modals_and_open("sources");
            }
        },
        text: function() {
            if ($scope.text_to_add && $scope.text_to_add.length > 0) {
                $scope.sources.push({
                    type: "text",
                    data: $scope.text_to_add
                });
                $scope.text_to_add = "";
                $scope.close_all_modals_and_open("sources");
            }
        }
    };


    $scope.push_polygons_back = function() {
        _.values(map._layers).forEach(function(layer){
            if (layer && layer._latlngs) {
                layer.bringToBack();
            }
        });
    }


    $scope.process_job = function() {
        console.log("starting process_job with $scope.share_url_element:", $scope.share_url_element);
        location.hash = $scope.job;
        $scope.share_url = location.origin + "/view_map/" + $scope.job;
        console.log("scope.share-Url:", $scope.share_url);
        $scope.check_downloadability_of_extension("csv");
        $scope.check_downloadability_of_extension("geojson");
        $scope.check_downloadability_of_extension("gif");
        $scope.check_downloadability_of_extension("jpg");
        $scope.check_downloadability_of_extension("pdf");
        $scope.check_downloadability_of_extension("png");
        $scope.check_downloadability_of_extension("shp");
        $scope.check_downloadability_of_metadata("iso_19115_2");
        $scope.load_modal_if_necessary("share").then(function() {
            $("#share_url").attr("href", $scope.share_url).text($scope.share_url);
        });
    };


    $scope.generate = function() {
        if ($scope.sources.length > 0) {

            // don't wait to load load modal before requesting a map
            // assuming that loading the modal is quicker than generating the map
            $scope.load_modal_if_necessary("load").then(function() {
                $scope.close_all_modals_and_open("load");
            });

            if($scope.countries) data.countries = $scope.countries.split(",").map(function(c){return c.trim();});
            if($scope.admin1limits) data.admin1limits = $scope.admin1limits.split(",").map(function(c){return c.trim();});

            // thx https://uncorkedstudios.com/blog/multipartformdata-file-upload-with-angularjs
            var formData = new FormData();
            formData.append('max_time', $scope.max_time);

            $scope.sources.forEach(function(source, index) {
                formData.append("source_" + index + "_type", source.type);
                formData.append("source_" + index + "_data", source.data);
            });

            $http.post('/request_map_from_sources', formData, {
                transformRequest: angular.identity,
                headers: {'Content-Type': undefined}
            }).then(function(response) {
                $scope.job = response.data;

                if (localStorage['maps']) {
                    $scope.previous_maps = [$scope.job].concat(_.without(localStorage['maps'].split(","), $scope.job));
                } else {
                    $scope.previous_maps = [ $scope.job ];
                }
                localStorage['maps'] = $scope.previous_maps.join(",");

                $scope.process_job();
                $scope.get_map_when_ready();
            });
        }
    };

    $scope.clear_recent_maps = () => {
        $scope.previous_Maps = [];
        localStorage.removeItem("maps");
    };

    $scope.features = [];
    $scope.correct_features = [];
    $scope.features_that_appear_in_table = [];
    $scope.max_time = 10;

    map = L.map('map');

    /*
    L.Voice.commands.switch_basemap = {
        pattern: L.Voice.commands.switch_basemap.pattern,
        action: function() {
            close_all_modals_and_open("basemaps");
        }
    };

    L.Voice.commands.close = {
        pattern: L.Voice.patterns.close,
        action: function() {
            close_all_modals();
        }
    };
    */ 

    $scope.easy_buttons = {};

    // add button to zoom out to globe
    L.easyButton('<span class="glyphicon glyphicon-globe" style="font-size: 14pt; top: 4px;"></span>', function(btn, map){
        map.setView([0,0], 1);
    }).addTo(map);

    // add button to add place
    $scope.easy_buttons.add = L.easyButton('<span class="glyphicon glyphicon-map-marker" title="Add Place" style="font-size: 14pt; top: 4px;"></span>', function(btn, map){
        console.log("adding place");
        $scope.close_all_modals_and_open("add");
    });

    /*L.easyButton('<span class="glyphicon glyphicon-search" style="font-size: 14pt; top: 4px;"></span>', function(btn, map){
        console.log("searching");
    }).addTo(map);*/


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

    // basemaps button
    var BasemapsControl = L.Control.extend({
        options: {
            position: "bottomright",
        },
        onAdd: function(map) {
            var basemapsButton = L.DomUtil.create("div", "leaflet-bar leaflet-control leaflet-control-custom");
            basemapsButton.style.boxShadow = 'none';
            basemapsButton.id = "showBasemapsModalControl";
            basemapsButton.innerHTML = "<div><button type='button' id='basemapsButton' class='btn btn-primary btn-xs' onclick='close_all_modals_and_open(\"basemaps\")' style='width: 100px'>Basemaps</button></div>";
            return basemapsButton;
        }
    });
    $scope.basemapsControl = new BasemapsControl();

    map.setView([0,0],2);

    $scope.clear_layers = function(skip_basemaps=false) {
        map.eachLayer(function(layer) {
            if(!(skip_basemaps && layer._url)) { // skipping over basemaps
                map.removeLayer(layer);
            }
        });
        // hack to force renderer to reset width and height of svgs when drawing next
        //https://github.com/Leaflet/Leaflet/blob/cbaf02034c916e0e3ea1f1f5c21d08c41efd0b3e/src/layer/vector/SVG.js#L90
        map._renderer._svgSize = null;
   };

    $scope.clear_everything = function() {
        console.log("starting clear_everything");
        $scope.clear_layers(skip_basemaps=false);
        $scope.correct_features = [];
        $scope.countries = "";
        $scope.admin1limits = "";
        $scope.features = [];
        $scope.features_that_appear_in_table = [];
        $scope.name_of_place_to_add = null;
        $scope.show_advanced_options = false;
        $scope.start_file = null;
        $scope.start_text = "";
        $scope.urls_to_files = "";
        $scope.urls_to_webpages = "";
        $scope.verified = false;
        window.location.hash = "";
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

    $scope.get_map_when_ready = function() {
        console.log("starting get_map_when_ready");
        function stop() { $interval.cancel(request);};
        var request = $interval( function(){
            console.log("checking if", $scope.job, "is ready"); 
            $http.get("/api/orders/" + $scope.job + "/?format=json&fields=complete").then(response => {
                if (response.data.complete) {
                    stop();
                    $scope.getFeatures();
                    $scope.getMetaData();
                }
            });
        }, 2000);
    };

    $scope.check_downloadability_of_extension = function(extension) {

        var original_job = $scope.job;

        function stop() { $interval.cancel(request); };

        var request = $interval( function(){
            if ($scope.job == original_job) {
                console.log("checking if", $scope.job, extension, "is ready");
                $scope.load_modal_if_necessary("download").then(function() {
                    $scope["download_link_" + extension] = location.origin + "/get_map/" + $scope.job + "/" + extension;
                });
                $http.get('/does_map_exist/' + $scope.job + "/" + extension).then(function(response) {
                    console.log("got response", response);
                    if (response.data === "yes") {
                        stop();
                        $scope["ready_to_download_" + extension] = true;
                    } else {
                        $scope["ready_to_download_" + extension] = false;
                    }
                });
            }
        }, 2000);
    }; 

    $scope.verify_map = function() {
        if (!$scope.verified) {
           $http.patch("/api/features/verify/?order__token=" + $scope.job).then(response => {
                if (response.data.status === "success") {
                    $scope.verified = true;
                }
            });
        }
    };

    $scope.check_downloadability_of_metadata = function(metadata) {
        return;
        function stop() { $interval.cancel(request); };

        var request = $interval( function(){
            console.log("checking downloadability of metadata", $scope.job, metadata);
            document.getElementById("download_metadata_link_" + metadata).href = location.origin + "/get_metadata/" + $scope.job + "/" + metadata;
            $http.get('/does_metadata_exist/' + $scope.job + "/" + metadata).then(function(response) {
                console.log("got response", response);
                if (response.data === "yes") {
                    stop();
                    $scope["ready_to_download_metadata_" + metadata] = true;
                } else {
                    $scope["ready_to_download_metadata_" + metadata] = false;
                }
            });
        }, 2000);
    }; 




    $scope.fixLocationUsingTheMap = fixLocation = function(feature) {

        console.log("starting fixLocation with feature id of ", feature);

        document.getElementById("map-alert").textContent = "Fixing " + feature.name;
        centerControl.show();

        $scope.mode = "fixing";

        modals.fix.modal("hide");

        var name = feature.name;

        var options = $scope.features.filter(function(feature) {
            return feature.name === name;
        });

        console.log("OPTIONS:", options);

        // hide all the other locations
        $scope.features_that_appear_in_table = options;

        // clear map
        $scope.clear_layers(skip_basemaps=true);


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
                    var url = location.origin + "/api/change_featureplace";
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
                var polygon = L.polygon(turf.flip(turf.helpers.polygon(feature.polygon)).geometry.coordinates, getStyle(feature)).addTo(map);
                polygon.on("click", onclick(feature));
                polygon.on("mouseover", onmouseover);
                polygon.on("mouseout", onmouseout);
                $scope.featureGroup.addLayer(polygon);
            }

            if (feature.multipolygon) {
                var multipolygon = L.polygon(turf.flip(turf.helpers.multiPolygon(feature.multipolygon)).geometry.coordinates, getStyle(feature)).addTo(map);
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

        var map_elements = [];
    
        $scope.correct_features = $scope.features.filter(function(feature){return feature.correct;});
        $scope.correct_features.forEach(function(feature) {

            var popup_html = "<div style='text-align:center'><b>"+feature.name+"</b></div>" +
                "<div><b>Latitude:</b> " + $scope.numberToString(feature.latitude) + "</div>"
                + "<div><b>Longitude:</b> " + $scope.numberToString(feature.longitude) + "</div>"
                + "<button type='button' class='btn btn-warning btn-xs' onclick='displayStyleModalById(" + feature.featureplace_id + ")' style='margin: 5px;     background-color: purple; border: hotpink;'>Style</button>"
                + "<button type='button' class='btn btn-warning btn-xs' onclick='displayFixModalById(" + feature.featureplace_id + ")' style='margin: 5px;'> Fix </button>"
                + "<button type='button' class='btn btn-primary btn-xs' onclick='displayEditModalById(" + feature.featureplace_id + ")' style='margin: 5px;'>More</button>"
                + "<button type='button' class='btn btn-danger btn-xs pull-right' onclick='deleteByFeaturePlaceIdFromPopup(" + feature.featureplace_id + ")' style='margin: 5px;'>Delete</button>";

            var popup_options = {
                'maxWidth': '500',
                'className' : 'custom-popup'
            };

            var geom_used = feature.geometry_used.toLowerCase();
              
            var marker = L.circleMarker([feature.latitude, feature.longitude], getStyle(feature));
            marker.feature_id = feature.feature_id;
            marker.featureplace_id = feature.featureplace_id;
            marker.bindPopup(popup_html, popup_options);
            marker.addTo(map);

            if (feature.style.label) {
                marker.bindTooltip(feature.name, {
                    className: "place-label",
                    permanent: true
                });
            }
            map_elements.push(marker);

            // hide point if not supposed to show it, but still need it on the map in order to place the label correctly
            // when you have multipolygon's the label sometimes is placed on the wrong polygon, like an island instead of the mainland
            if (!geom_used.includes("point")) {
                marker.setStyle({
                    "fillOpacity": 0,
                    "opacity": 0
                });
            }

            if (geom_used.includes("shape")) {
                if (feature.polygon) {
                   console.log("creating polygon for", feature);
                    var polygon = L.polygon(turf.flip(turf.helpers.polygon(feature.polygon)).geometry.coordinates, getStyle(feature)).addTo(map);
                    polygon.feature_id = feature.feature_id;
                    polygon.featureplace_id = feature.featureplace_id;
                    polygon.bindPopup(popup_html, popup_options);
                    polygon.addTo(map);
                    map_elements.push(polygon);
                    console.log("pushed", polygon);
                } else if (feature.multipolygon) {
                    console.log("creating multipolygon for", feature);
                    var multipolygon = L.polygon(turf.flip(turf.helpers.multiPolygon(feature.multipolygon)).geometry.coordinates, getStyle(feature)).addTo(map);
                    multipolygon.feature_id = feature.feature_id;
                    multipolygon.featureplace_id = feature.featureplace_id;
                    multipolygon.bindPopup(popup_html, popup_options);
                    multipolygon.addTo(map);
                    map_elements.push(multipolygon);
                    console.log("pushed", multipolygon);
                }
            }

        });
        $scope.push_polygons_back();
        $scope.features_that_appear_in_table = $scope.correct_features;
        if (map_elements.length > 0) {
            map.fitBounds(L.featureGroup(map_elements).getBounds().pad(0.01));
        } else {
            map.setView([0,0], 1);
        }
        if (modals.load) modals.load.modal("hide");
    };

    $scope.getFeatures = function() {
        $http.get(location.origin + "/api/feature_data/" + $scope.job).then(function(response) {
            var basemap_code = response.data.style.basemap_code;
            if (basemap_code == "Blank") {
                $scope.basemap = null;
            } else {
                $scope.basemap = L.tileLayer.provider(basemap_code).addTo(map);
            }
            $scope.features = response.data.features;
            $scope.loadFeatures();
        });
    };

    $scope.getMetaData = function() {
        $http.get(location.origin + "/api/metadata/" + $scope.job).then(function(response) {
            $scope.metadata = response.data.metadata;
        });
    };

    $scope.deleteSelection = function() {
        console.log("starting delete selection with", $scope.selection);
        var featureplace_id = $scope.selection.featureplace_id;
        $scope.deleteByFeaturePlaceId(featureplace_id);
    };

    $scope.deleteByFeaturePlaceId = deleteByFeaturePlaceId = function(featureplace_id) {
        console.log("starting deleteByFeaturePlaceId with", featureplace_id);
        $http.post(location.origin + "/api/change_featureplace", {featureplace_id: featureplace_id, correct: false}).then(function(response) {
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
        if (modals.edit) modals.edit.modal("hide"); //if haven't loaded an edit modal before, then obviously don't have to hide it
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
        $scope.load_modal_if_necessary("edit").then(() => {
            // need to set the selection after the modal loads because it will override entity properties with loaded from template via ng-model
            if (entity) $scope.selection = entity;
            modals.edit.modal();
        });
    };

    $scope.select = function(featureplace_id) {
        $scope.$apply(function(){
            $scope.selection = _.find($scope.features, function(feature) { return feature.featureplace_id === featureplace_id; });
        });
    };

    $scope.select_basemap = function(basemap) {
        console.log("starting select_map with", basemap);


        var old_basemap = $scope.basemap;
        if (basemap.code == "Blank") {
            var new_basemap = null;
        } else {
            var new_basemap = L.tileLayer.provider(basemap.code).addTo(map);
        }

        if (old_basemap) map.removeLayer(old_basemap);
        $scope.basemap = new_basemap;


        // only try to change if actually in a job
        // could just try to change basemap in free view
        // before start creating a map
        if ($scope.job) {
            var url = location.origin + "/api/change_basemap";
            $http.post(url, { id: basemap.id, token: $scope.job });
        }

        close_all_modals();
    };

    $scope.displayEditModalById = displayEditModalById = function(featureplace_id) {
        $scope.select(featureplace_id);
        modals.edit.modal();
    };

    $scope.displayFixModalById = displayFixModalById = function(featureplace_id) {
        $scope.select(featureplace_id);
        $scope.load_modal_if_necessary("fix").then(() => {
            modals.fix.modal();
        });
    };

    $scope.displayStyleModalById = displayStyleModalById = function(featureplace_id) {
        $scope.select(featureplace_id);
        modals.style.modal();
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

    $scope.changeStyle = function() {
        console.log("selection is ", selection);
        //var new_style = selection.style;
        //var marker = _.find(_.values(map._layers), lyr => lyr._point && lyr.feature_id == 3358);
        //if (new_style.label
        
    }


    console.log("finishing MegaController");

    if (location.hash.length > 5) {
        $scope.job = location.hash.replace("#","");
        $scope.process_job();
        $scope.get_map_when_ready();
        if (localStorage['maps']) {
            $scope.previous_maps = [$scope.job].concat(_.without(localStorage['maps'].split(","), $scope.job));
        } else {
            $scope.previous_maps = [$scope.job];
        }
        localStorage['maps'] = $scope.previous_maps.join(",");
    } else {
        $scope.previous_maps = localStorage['maps'] ? localStorage['maps'].split(",") : [];
        modals.start.modal();
    }


    // AFTER START MODAL APPEARS

    $scope.update_settings = function() {
        try {
            console.log("starting update_settings");

            var settings = $scope.settings;

            var basemapsButton = document.getElementById("basemapsButton");
            if (settings.basemaps) {
                if (!basemapsButton) {
                    map.addControl($scope.basemapsControl);
                }
            } else {
                if (basemapsButton) {
                    $scope.basemapsControl.remove();
                }
            }


            if (!$scope.fullscreen_control) {
                $scope.fullscreen_control = new L.Control.Fullscreen();
            }
      
            var fullscreen_element = map._controlContainer.querySelector(".leaflet-control-fullscreen");
            if (settings.fullscreen) {
                if (!fullscreen_element) {
                    map.addControl($scope.fullscreen_control);
                }
            } else {
                if (fullscreen_element) {
                    $scope.fullscreen_control.remove();
                }
            }


            if(!$scope.voice_control) {
                $scope.voice_control = new L.Control.Voice();
            }

            var element = map._controlContainer.querySelector(".leaflet-control-voice-commands");
            if(settings.voice) {
                if (!element) {
                    map.addControl($scope.voice_control);
                }
            } else {
               if (element) {
                   $scope.voice_control.remove();
               }
            }

            localStorage['settings'] = JSON.stringify(settings);
        } catch (error) {
            console.error(error);
        }

    };
    $scope.update_settings();




    $http.get(location.origin + "/api/basemaps/?format=json&limit=1000").then(function(response) {
        $scope.basemaps = _.sortBy(response.data.results.map(function(basemap) {
            return {
                code: basemap.name,
                id: basemap.id,
                name: basemap.name.replace(/\./g, " ").replace(/([a-z])([A-Z])/g, '$1 $2').replace(/([A-Z])([A-Z])([a-z])/, '$1 $2$3').replace(/ ([a-z])/g, s => s.toUpperCase()).replace(" And ", " and ").replace("Open Street Map", "OpenStreetMap")
            };
        }), basemap => basemap.name);
    });

    $scope.openMap = function (token) {
        console.log("starting getRecentUrl with", token);
        $scope.clear_everything();
        $scope.job = token;
        $scope.process_job();
        $scope.get_map_when_ready();
        close_all_modals();
   };

    $scope.closeAddModal = function() {
        close_all_modals();
        $scope.name_of_place_to_add = null;
    };

    $scope.getTypeAheadOptions = (viewValue) => $http.get('/api/places/typeahead/?name=' + viewValue).then(response => response.data);

    $scope.updateAddOptions = function($item, $model, $label, $event) {
        console.log("starting updateAddOptions", $scope.name_of_place_to_add);
        //$http.get('/api/places/?limit=100&name=' + $scope.name_of_place_to_add).then(response => {
        $http.post("/request_possible_additions", {
            name: $scope.name_of_place_to_add,
            token: $scope.job
        }).then(response => {
            console.log("response:", response);
            var data = response.data;
            //$scope.max_slides = data.count;
            var width_of_carousel = $("[uib-carousel]").width();
            //var width_of_sides = $(".left.carousel-control").width() + $(".right.carousel-control").width();
            var width_of_sides = width_of_carousel * 0.15 * 2;
            var width_available = width_of_carousel - width_of_sides;
            var number_per_group = Math.floor(width_available / 200);
            console.log("number_per_group:", number_per_group);
            $scope.groups = [];
            data.forEach(result => {
                var last_group = _.last($scope.groups);
                if (last_group && last_group.length < number_per_group) {
                    last_group.push(result);
                } else {
                    $scope.groups.push([result]);
                }
            });
        });
    };

    $scope.activeSlide = 0;
    //$scope.$watch("activeSlide", () => {console.log("activeSlide changed"); $scope.mini_maps[$scope.activeSlide]._onResize()});
    $scope.$watch("activeSlide", function() {
        if (!isNaN($scope.activeSlide)) {
            var mini_map = $scope.mini_maps[$scope.activeSlide];
            //console.log("mini_map:", mini_map);
            if (mini_map) {
                mini_map._onResize();
            }
        }
    });

    $scope.mini_maps = [];
    $scope.create_mini_map = function (option) {
        console.log("starting create_mini_map with", option);
        console.log("el:", document.getElementById("mini-map-" + option.id));
        var coordinates = option.point.coordinates;
        var latlng = [coordinates[1], coordinates[0]];
        var mini_map = L.map("mini-map-" + option.id, {
            boxZoom: false,
            center: latlng,
            doubleClickZoom: false,
            dragging: false,
            scrollWheelZoom: false,
            tap: false,
            touchZoom: false,
            zoom: 3,
            zoomControl:false
        });
        $scope.mini_maps.push(mini_map); 

        $scope.promise_to_create_leaflet_clone_layer.then(function() {
            _.values(map._layers).forEach(function(layer) {
                try {
                    //skipping over tooltips because they would clog such a small map screen
                    if (!(layer instanceof L.Tooltip)) {
                        cloneLayer(layer).addTo(mini_map);
                    }
                } catch (error) {
                    console.error(error);
                    console.error(layer);
                }
            });

            var icon = L.ExtraMarkers.icon({
                icon: 'glyphicon-star',
                markerColor: 'red',
                shape: 'square',
                prefix: 'glyphicon'
            });
            L.marker(latlng, {icon: icon}).addTo(mini_map);
        });
    };


    $scope.create_mini_maps = function() {
        console.log("starting create_mini_maps");
    };

    $scope.promise_to_create_leaflet_clone_layer = load_script("static/node_modules/leaflet-clonelayer/index.js");

  } catch (err) { console.error(err); }

}]);
