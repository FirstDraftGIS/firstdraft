app.controller('UploadController', ['$scope', '$http', '$window', '$compile', '$element', function($scope, $http, $window, $compile, $element) {

    $scope.upload = function(){
        console.log("starting upload");
        console.log("$scope.start is", $scope.start);
        if ($scope.start === 'paste')
        {
            $http
            .post('/upload', {'story': $scope.story}).
            then(function(response) {
                console.log("Response is", response);
                $scope.$parent.job = $scope.job = response.data;
                console.log("$scope.$parent is", $scope.$parent);
            });
        }
        else if ($scope.start === 'upload')
        {
            // thx https://uncorkedstudios.com/blog/multipartformdata-file-upload-with-angularjs
            var fd = new FormData();
            fd.append('file', $scope.upload_file);
            $http
            .post('/upload_file', fd, {
                transformRequest: angular.identity,
                headers: {'Content-Type': undefined}
            }).
            then(function(response) {
                console.log("Response is", response);
                $scope.$parent.job = $scope.job = response.data;
                console.log("$scope.$parent is", $scope.$parent);
            });
        }
    };
}]);

