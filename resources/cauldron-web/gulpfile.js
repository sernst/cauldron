var gulp = require('gulp');
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');
var es = require('event-stream');
var bowerData = require('./bower.json');
var addSrc = require('gulp-add-src');
var cleanCss = require('gulp-clean-css');
var sass = require('gulp-sass');

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
      .pipe(concat('project.js'))
      .pipe(gulp.dest(destRoot));
});

gulp.task('build-css', function () {

  var sassStream = gulp.src('app/style/app.scss')
        .pipe(sass().on('error', sass.logError));

  var files = bowerData.__installs__.css.map(function (item) {
    return 'bower_components/' + item;
  });
  files.push('app/style/**/*.css');

  return es.merge(sassStream, gulp.src(files))
      .pipe(cleanCss())
      .pipe(concat('project.css'))
      .pipe(gulp.dest(destRoot));
});

gulp.task('build-html', function () {
  return gulp.src('app/*.html')
      .pipe(gulp.dest(destRoot));
});


gulp.task('copy-icons', function () {
  return gulp.src('app/style/icons/*.*')
      .pipe(gulp.dest(destRoot + '/icons'));
});

gulp.task('build', [
  'copy-icons',
  'build-js',
  'build-css',
  'build-html'
]);
