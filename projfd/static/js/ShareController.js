app.controller('ShareController', ['$scope', '$http', '$window', '$compile', '$element', '$interval', function($scope, $http, $window, $compile, $element, $interval) {
    $scope.show_share_links = false;
    $scope.activate = function(){
        console.log("starting activate in share");
        a_share_link = document.getElementById('href_share_link');
        share_link = window.location.origin + '/view_map/' + $scope.$parent.job;
        a_share_link.innerHTML = a_share_link.href = share_link;
        $scope.show_share_links = true;
    };

    $scope.$on('show_downloads', function(event, args){
        console.log("show_downloads so activate sharing");
        $scope.activate();
    });
}]);

