app.controller('DownloadController', ['$scope', '$http', '$window', '$compile', '$element', function($scope, $http, $window, $compile, $element) {


    $scope.activate = function(){
        $scope.show_downloads = true;
        document.getElementById("href_geojson").href = $scope.href_geojson = "/maps/" + $scope.$parent.job + "/geojson";
        console.log("$scope.href_geojson is", $scope.href_geojson);
    };

    $scope.$on('show_downloads', function(event, args){
        console.log("show_downloads!, so activate");
        $scope.activate();
        //any other action can be perfomed here
    });
}]);

