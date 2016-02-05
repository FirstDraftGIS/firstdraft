Loader = function() {
    var exports = {};

    var spinnerContainer = exports.element = document.createElement("DIV");
    spinnerContainer.className = "spinnerContainer";

    var wrapper = document.createElement("DIV");
    wrapper.className = "spinnerWrapper";

    var spinner = document.createElement("DIV");
    spinner.className = "spinner";
    spinner.textContent = "generating map";
    wrapper.appendChild(spinner);

    spinner.appendChild(wrapper);

    var activate = exports.activate = function activate() {
        spinnerContainer.style.zIndex = "9999999";
        spinnerContainer.style.display = "block";
    };
    var deactivate = exports.deactivate = function deactivate() {
        spinnerContainer.style.zIndex = "-9999999";
        spinnerContainer.style.display = "none";
    };

    return exports;
}
