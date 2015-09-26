app.controller('UploadController', ['$scope', '$http', '$window', '$compile', '$element', function($scope, $http, $window, $compile, $element) {
    var inputWebpage = document.getElementById("url_to_webpage");
    var inputFile = document.getElementById("url_to_file");
    var textarea = document.getElementById("story");
    $scope.focusOnTextArea = function()
    {
        textarea.focus();
    };
    $scope.focusOnUrlToWebpageInput = function()
    {
        inputWebpage.focus();
    };
    $scope.focusOnUrlToFileInput = function()
    {
        inputFile.focus();
    };



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
        else if ($scope.start === 'url_to_webpage')
        {
            $http
            .post('/start_link', {'link': $scope.url_to_webpage}).
            then(function(response) {
                console.log("Response is", response);
                $scope.$parent.job = $scope.job = response.data;
                console.log("$scope.$parent is", $scope.$parent);
            });
        }
        else if ($scope.start === 'url_to_file')
        {
            $http
            .post('/start_link_to_file', {'link': $scope.url_to_file}).
            then(function(response) {
                console.log("Response is", response);
                $scope.$parent.job = $scope.job = response.data;
                console.log("$scope.$parent is", $scope.$parent);
            });
        }
    };
}]);

