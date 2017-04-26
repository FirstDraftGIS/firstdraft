app.controller('DownloadController', ['$scope', '$http', '$window', '$compile', '$element', '$interval', function($scope, $http, $window, $compile, $element, $interval) {


    $scope.activate = function(){
        $scope.show_downloads = true;
        document.getElementById("href_geojson").href = $scope.href_geojson = "/get_map/" + $scope.$parent.job + "/geojson";
        console.log("$scope.href_geojson is", $scope.href_geojson);


        $scope.stop_shp = function(){$interval.cancel(promise_shp);};
        $scope.stop_csv = function(){$interval.cancel(promise_csv);};

        var promise_shp = $interval( function(){
            console.log("will request",'/does_map_exist/' + $scope.$parent.job + '/zip'); 
            $http.get('/does_map_exist/' + $scope.$parent.job + '/zip').then(function(response) {
                console.log("got from does_map_exist", response);
                if (response.data === "True")
                {
                    $scope.stop_shp();
                    document.getElementById("href_shp").href = $scope.href_shp = "/get_map/" + $scope.$parent.job + "/zip";
                }
            });
        }, 2000);

        var promise_csv = $interval( function(){
            console.log("will request",'/does_map_exist/' + $scope.$parent.job + '/csv'); 
            $http.get('/does_map_exist/' + $scope.$parent.job + '/csv').then(function(response) {
                console.log("got from does_map_exist", response);
                if (response.data === "True")
                {
                    $scope.stop_csv();
                    document.getElementById("href_csv").href = $scope.href_csv = "/get_map/" + $scope.$parent.job + "/csv";
                }
            });
        }, 2000);

    };


    $scope.$on('show_downloads', function(event, args){
        console.log("show_downloads!, so activate");
        $scope.activate();
        //any other action can be perfomed here
    });
}]);

