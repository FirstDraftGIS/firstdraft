app.controller('MegaController', ['$scope', '$http', '$window', '$compile', '$element', '$interval', function($scope, $http, $window, $compile, $element, $interval) {

    console.log("starting MegaController");

    $('#download_link_csv').href = '/get_map/' + job + '/csv';
    $('#download_link_geojson').href = '/get_map/' + job + '/geojson';
    $('#download_link_shp').href = '/get_map/' + job + '/zip';


    map = L.map('map', {"fullscreenControl": true});
    map.setView([0,0],2);
    L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors.',
        maxZoom: 18
    }).addTo(map);
    

    var mainLayerStyle = {
        "color": "#ff0000",
        "weight": .5,
        "opacity": .5,
        "fillOpacity": 0
    };

    function onEachFeature(feature, layer) {
        try {
            p = feature.properties;
            console.log("properties are", p);
            var popup_html = "<div style='max-height: 250px; overflow-y: auto;'>";
            popup_html += "<h3>" + (p.name || p.location);
            if (p.date_pretty) popup_html += " (" + p.date_pretty + ")";
            popup_html += "</h3>";
            if(p.confidence) popup_html += "<b>confidence: </b>" + p.confidence + "</br>";
            if(p.admin_level) popup_html += "<b>admin level: </b>" + p.admin_level + "</br>";
            if(p.pcode) popup_html += "<b>pcode: </b>" + p.pcode + "</br>";
            if(p.geonameid) popup_html += "<b>geonameid: </b>" + p.geonameid + "</br>";
            if(p.context) popup_html += "<p><b>context: </b>" + p.context + "</p>";
            popup_html += "</div>";
            layer.bindPopup(popup_html);
        }
        catch(err) { console.error("err is", err); }
    }

    var mainLayer = L.geoJson(undefined,{onEachFeature:onEachFeature, style:mainLayerStyle});
    var featureGroup = L.featureGroup([mainLayer]);
    featureGroup.addTo(map);
    map.setView([0,0],2);

    $.getJSON('/get_map/'+job+'/geojson', function( data ) {
        mainLayer.addData(data);
    });

    console.log("finishing MegaController");

}]);
