var gulp = require('gulp');
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');
var es = require('event-stream');
var bowerData = require('./bower.json');
var addSrc = require('gulp-add-src');
var cleanCss = require('gulp-clean-css');

var destRoot = '../web';

gulp.task('build-js', function () {
  var bowerFiles = bowerData.__installs__;

  var bowerStream = gulp.src(bowerFiles.js.map(function (item) {
    return 'bower_components/' + item;
  }))
      .pipe(uglify());

  var jsMinStream = gulp.src(bowerFiles.js_min.map(function (item) {
    return 'bower_components/' + item;
  }));

  var myStream = gulp.src([
    'app/js/initialize.js',
    'app/js/app/**/*.js',
    'app/js/run.js'
  ])
      .pipe(uglify());

  return es.merge(jsMinStream, bowerStream, myStream)
      .pipe(concat('report.js'))
      .pipe(gulp.dest(destRoot));
});

gulp.task('build-css', function () {
  var files = bowerData.__installs__.css.map(function (item) {
    return 'bower_components/' + item;
  });
  files.push('app/style/**/*.css');

  return gulp.src(files)
      .pipe(cleanCss())
      .pipe(concat('report.css'))
      .pipe(gulp.dest(destRoot))
});

gulp.task('build-html', function () {
  gulp.src('app/*.html')
      .pipe(gulp.dest(destRoot));
});


gulp.task('build', [
  'build-js',
  'build-css',
  'build-html'
]);
