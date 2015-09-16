app.controller('UploadController', ['$scope', '$http', '$window', '$compile', '$element', function($scope, $http, $window, $compile, $element) {

    $scope.upload = function(){
        console.log("starting upload");
        console.log("story is", $scope.story);

        $http
        .post('/upload', {'story': $scope.story}).
        then(function(response) {
            console.log("Response is", response);
            $scope.$parent.job = $scope.job = response.data;
            console.log("$scope.$parent is", $scope.$parent);
        });
    };
}]);

