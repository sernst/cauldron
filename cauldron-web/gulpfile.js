var gulp = require('gulp');
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');
var es = require('event-stream');
var bowerData = require('./bower.json');
var addSrc = require('gulp-add-src');
const cleanCss = require('gulp-clean-css');
const sass = require('gulp-sass');
const gulpif = require('gulp-if');
const minimist = require('minimist');
const rename = require('gulp-rename');
const babel = require('gulp-babel');
const sourcemaps = require('gulp-sourcemaps');
const iife = require('gulp-iife');

var destRoot = '../cauldron/resources/web';
var taskName = null;
process.argv.some(function (arg) {
  switch (arg) {
    case 'develop':
      taskName = 'develop';
      return true;

    case 'build':
      taskName = 'build';
      return true;
  }

  return false;
});


/**
 *
 */
gulp.task('build-js', function () {
  return gulp.src([
    'app/js/utils.js',
    'app/js/initialize.js',
    'app/js/app/**/*.js',
    'app/js/run.js'
  ])
    .pipe(gulpif(taskName === 'develop', sourcemaps.init()))
    .pipe(babel({ presets: ['es2015'] }))
    .pipe(gulpif(taskName === 'build', uglify()))
    .pipe(iife())
    .pipe(gulpif(taskName === 'develop', sourcemaps.write()))
    .pipe(concat('app.js'))
    .pipe(gulp.dest(destRoot + '/js'));
});


/**
 *
 */
gulp.task('copy-bower-components', function () {
  var copies = bowerData.__copies__;
  var streams = [];

  copies.forEach(function (copy) {
    var outputDirectory = destRoot + '/components/' + copy.name;
    Object.keys(copy.files).forEach(function (name) {
      streams.push(
          gulp.src('bower_components/' + copy.files[name])
              .pipe(rename(name))
              .pipe(gulp.dest(outputDirectory))
      );
    });

    Object.keys(copy.directories).forEach(function (name) {
      streams.push(
          gulp.src('bower_components/' + copy.directories[name] + '/**/*')
            .pipe(gulp.dest(outputDirectory + '/' + name))
      );
    });
  });

  return es.merge.apply(null, streams);
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
      .pipe(gulp.dest(destRoot + '/js'));
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
      .pipe(gulp.dest(destRoot + '/css'));
});

/**
 *
 */
gulp.task('copy-css-resources', function () {

  var files = bowerData.__installs__.css_resources.map(function (item) {
    return 'bower_components/' + item;
  });

  return gulp.src(files).pipe(gulp.dest(destRoot + '/css'));
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
      .pipe(gulp.dest(destRoot + '/css/icons'));
});


var pre = [
  'copy-icons',
  'build-bower-js',
  'build-js',
  'build-css',
  'build-html',
  'copy-css-resources',
  'copy-bower-components'
];

gulp.task('develop', pre);
gulp.task('build', pre);
