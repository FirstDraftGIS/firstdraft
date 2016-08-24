app = angular.module('app', ['ui.bootstrap','ui.grid','ui.grid.pagination','ui.grid.selection']);

console.log("app is", app);
app.directive('ngEnter', function () {
    return function (scope, element, attrs) {
        element.bind("keydown keypress", function (event) {
            if(event.which === 13) {
                event.target.blur(); //effect is hiding softkeyboard on android
                scope.$apply(function (){
                    scope.$eval(attrs.ngEnter);
                });
                event.preventDefault();
            }
        });
    };
});
app.directive('fileModel', ['$parse', function ($parse) {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            var model = $parse(attrs.fileModel);
            var modelSetter = model.assign;
            
            element.bind('change', function(){
                scope.$apply(function(){
                    modelSetter(scope, element[0].files[0]);
                });
            });
        }
    };
}]);
app.service('fileUpload', ['$http', function ($http) {
    this.uploadFileToUrl = function(file, uploadUrl){
        var fd = new FormData();
        fd.append('file', file);
        $http.post(uploadUrl, fd, {
            transformRequest: angular.identity,
            headers: {'Content-Type': undefined}
        })
        .success(function(){
        })
        .error(function(){
        });
    }
}]);

function insertAfter(newNode, referenceNode) {
    referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
}

//return human readable content for object
function cleanObject(obj)
{
    for (var key in obj)
    {
        var value = obj[key];
        if (key === "language")
        {
            if(value === "en")
            {
                obj[key] = "English";
            }
            else if (value === "ar")
            {
                obj[key] = "Arabic";
            }
        }
        else if (key.indexOf("date") > -1)
        {
            if(value && typeof value === "string")
            {
                obj[key] = value.split("T")[0];
            }
        }
    }
    return obj;
}

function removeA(arr) {
    var what, a = arguments, L = a.length, ax;
    while (L > 1 && arr.length) {
        what = a[--L];
        while ((ax= arr.indexOf(what)) !== -1) {
            arr.splice(ax, 1);
        }
    }
    return arr;
}
