var gulp = require("gulp");
var concat = require("gulp-concat");
var del = require('del');
var insert = require('gulp-insert');
var less = require('gulp-less');
var path = require('path');
var request = require('request');

var paths = {
    scripts: ['src/*']
};

gulp.task("build", ["clean"], function() {


    request('https://api.mapbox.com/mapbox.js/plugins/leaflet-fullscreen/v1.0.1/Leaflet.fullscreen.min.js', function (error, response, body) {
        console.log('body:', body); // Print the HTML for the Google homepage.
        gulp.src([
        "./node_modules/underscore/underscore-min.js",
        "./node_modules/jquery/dist/jquery.min.js",
        "./node_modules/bootstrap/dist/js/bootstrap.min.js",
        "./node_modules/leaflet/dist/leaflet.js"
        //"./node_modules/jquery-ui/build/release.js"
        //"./node_modules/angular/angular.min.js"
        ])
        .pipe(concat("external.js", {newLine: '\n\n\n\n\n\n'}))
        .pipe(insert.append("\n\n\n\n" + body))
        .pipe(gulp.dest("dist/js/"));
    });    
});

// Not all tasks need to use streams
// A gulpfile is just another node program and you can use any package available on npm
gulp.task('clean', function() {
    // You can use multiple globbing patterns as you would with `gulp.src`
    return del(['dist/js/']);
});

gulp.task("less", function() {
    return gulp.src('./less/**/*.less')
    .pipe(less({
      paths: [ path.join(__dirname, 'less', 'includes') ]
    }))
    .pipe(gulp.dest('./dist/css'));
});

// Rerun the task when a file changes
gulp.task('watch', function() {
    gulp.watch("./*", ['less', 'build']);
});

// The default task (called when you run `gulp` from cli)
gulp.task('default', ['watch', 'build', 'less']);
