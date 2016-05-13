var gulp = require('gulp');
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');
var es = require('event-stream');
var bowerData = require('./bower.json');
var addSrc = require('gulp-add-src');
var cleanCss = require('gulp-clean-css');
var sass = require('gulp-sass');
var gulpif = require('gulp-if');
var minimist = require('minimist');

var taskName = process.argv[1];
var destRoot = '../web';

/**
 *
 */
gulp.task('build-js', function () {
  return gulp.src([
    'app/js/initialize.js',
    'app/js/app/**/*.js',
    'app/js/run.js'
  ])
      .pipe(gulpif(taskName === 'build', uglify()))
      .pipe(concat('app.js'))
      .pipe(gulp.dest(destRoot));
});

/**
 *
 */
gulp.task('build-bower-js', function () {
  var bowerFiles = bowerData.__installs__;

  var bowerStream = gulp.src(bowerFiles.js.map(function (item) {
    return 'bower_components/' + item;
  }))
      .pipe(gulpif(taskName === 'build', uglify()));

  var jsMinStream = gulp.src(bowerFiles.js_min.map(function (item) {
    return 'bower_components/' + item;
  }));

  var extStream = gulp.src('app/js/ext/**/*.js');

  return es.merge(jsMinStream, bowerStream, extStream)
      .pipe(concat('bower.js'))
      .pipe(gulp.dest(destRoot));
});


/**
 *
 */
gulp.task('build-css', function () {

  var sassStream = gulp.src('app/style/app.scss')
        .pipe(sass().on('error', sass.logError));

  var files = bowerData.__installs__.css.map(function (item) {
    return 'bower_components/' + item;
  });
  files.push('app/style/**/*.css');

  return es.merge(sassStream, gulp.src(files))
      .pipe(gulpif(taskName === 'build', cleanCss()))
      .pipe(concat('project.css'))
      .pipe(gulp.dest(destRoot));
});


/**
 *
 */
gulp.task('build-html', function () {
  return gulp.src('app/*.html')
      .pipe(gulp.dest(destRoot));
});


/**
 *
 */
gulp.task('copy-icons', function () {
  return gulp.src('app/style/icons/*.*')
      .pipe(gulp.dest(destRoot + '/icons'));
});


var pre = [
  'copy-icons',
  'build-bower-js',
  'build-js',
  'build-css',
  'build-html'
];

gulp.task('develop', pre);
gulp.task('build', pre);
