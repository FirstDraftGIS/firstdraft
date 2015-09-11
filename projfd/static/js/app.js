app = angular.module('app', ['ui.bootstrap']);

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
