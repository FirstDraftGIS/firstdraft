app.controller('MagicController', ['$scope', '$http', '$window', '$compile', '$element', function($scope, $http, $window, $compile, $element) {

    $scope.hash = null;

    $scope.$watch('job', function(newValue, oldValue){
        console.log("watching job", newValue);
        if(newValue!=oldValue)
            $scope.$broadcast('uploaded',{"job":newValue});
    });

    $scope.$watch('show_downloads', function(newValue, oldValue){
        console.log("watching show_downloads", newValue);
        if(newValue!=oldValue)
            $scope.$broadcast('show_downloads');
    });
}]);

