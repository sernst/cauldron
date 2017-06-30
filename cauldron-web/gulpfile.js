const babel = require('gulp-babel');
const bowerData = require('./bower.json');
const cleanCss = require('gulp-clean-css');
const concat = require('gulp-concat');
const dedupe = require('gulp-dedupe');
const del = require('del');
const gulp = require('gulp');
const gulpif = require('gulp-if');
const iife = require('gulp-iife');
const merge = require('merge-stream');
const rename = require('gulp-rename');
const sass = require('gulp-sass');
const sourcemaps = require('gulp-sourcemaps');
const uglify = require('gulp-uglify');
const args = require('yargs').argv;

const isDevelop = args.develop;
const isProduction = !isDevelop;
console.log(isDevelop, isProduction);

/**
 * Creates a relative path to the a location within the root destination
 * directory for deployment
 *
 * @param segments
 *  Zero or more folder or file elements specifying a location within the
 *  root destination directory
 * @returns {string}
 *  The assembled destination path
 */
function makeDestinationPath(...segments) {
  return ['..', 'cauldron', 'resources', 'web']
    .concat(segments)
    .join('/');
}


/**
 * Returns a gulp stream destination targeting a location within the root
 * destination directory specified by the segment arguments
 *
 * @param segments
 *  Zero or more folder or file elements specifying a location within the
 *  root destination directory
 * @returns {*}
 *  A gulp stream destination for the given destination location
 */
function getStreamOutput(...segments) {
  return gulp.dest(makeDestinationPath(...segments));
}


/**
 * TASK: javascript
 *    Deploys the application JavaScript files by bundling them into a single
 *    app.js file with appropriate modifications depending on the task
 */
function javascript() {
  return gulp.src([
    'app/js/app/utils.js',
    'app/js/initialize.js',
    'app/js/app/**/*.js',
    'app/js/run.js'
  ])
    .pipe(dedupe())
    .pipe(gulpif(isDevelop, sourcemaps.init()))
    .pipe(babel({ presets: ['es2015'] }))
    .pipe(gulpif(isProduction, uglify()))
    .pipe(iife())
    .pipe(concat('app.js', { newLine: '\n' }))
    .pipe(gulpif(isDevelop, sourcemaps.write()))
    .pipe(getStreamOutput('js'));
}
exports.javascript = javascript;


/**
 * TASK: copyBowerComponents
 *    For each Cauldron component installed via bower and specified in the
 *    bower.json file, the component files are copied to their destination
 *    component folder according to the component entry in the bower.json file
 */
function copyBowerComponents() {
  const copies = bowerData.appCopies;
  const streams = copies
    .map((copyEntry) => {
      const files = Object.keys(copyEntry.files).map((filename) => {
        const sourcePath = copyEntry.files[filename];

        return gulp.src(`bower_components/${sourcePath}`)
          .pipe(rename(filename))
          .pipe(getStreamOutput('components', copyEntry.name));
      });

      const directories = Object.keys(copyEntry.directories).map((name) => {
        const sourceFolder = copyEntry.directories[name];

        return gulp.src(`bower_components/${sourceFolder}/**/*`)
          .pipe(getStreamOutput('components', copyEntry.name, name));
      });

      return files.concat(directories);
    })
    .reduce((flattened, streamList) => flattened.concat(streamList), []);

  return merge(...streams);
}
exports.copyBowerComponents = copyBowerComponents;


/**
 * TASK: javascriptExternal
 *    Copies external JavaScript files to the destination directory, minifying
 *    any files that are not already available in a minified format
 */
function javascriptExternal() {
  const installs = bowerData.appInstalls;
  const unminified = installs.js.map(item => `bower_components/${item}`);
  const minified = installs.jsMin.map(item => `bower_components/${item}`);

  const minifiedStream = gulp.src(minified);
  const externalStream = gulp.src('app/js/ext/**/*.js');
  const unminifiedStream = gulp.src(unminified)
    .pipe(gulpif(isProduction, uglify()));

  return merge(minifiedStream, unminifiedStream, externalStream)
      .pipe(concat('bower.js', { newLine: '\n' }))
      .pipe(getStreamOutput('js'));
}
exports.javascriptExternal = javascriptExternal;


/**
 * TASK: css
 *    Compiles the application SCSS files and concatenates them with
 *    external bower css files into a single CSS file
 */
function css() {
  const sassStream = gulp.src('app/style/app.scss')
        .pipe(sass().on('error', sass.logError));

  const files = bowerData.appInstalls.css
    .map(item => `bower_components/${item}`);
  files.push('app/style/**/*.css');

  return merge(sassStream, gulp.src(files))
      .pipe(gulpif(isProduction, cleanCss({ rebase: false })))
      .pipe(concat('project.css', { newLine: '\n' }))
      .pipe(getStreamOutput('css'));
}
exports.css = css;


/**
 * TASK: cssExternal
 *    Copies bower-based CSS resources such as images and fonts to their
 *    destination location
 */
function cssExternal() {
  const files = bowerData.appInstalls.cssResources
    .map((item) => `bower_components/${item}`);

  return gulp.src(files)
    .pipe(getStreamOutput('css'));
}
exports.copyCssResources = cssExternal;


/**
 * TASK: html
 *    Deploys HTML files to their destination locations
 */
function html() {
  return gulp.src('app/*.html')
      .pipe(getStreamOutput());
}
exports.html = html;


/**
 * TASK: copyIcons
 *    Copies all of the material design icon resources files
 */
function copyIcons() {
  return gulp.src('app/style/icon_font/*.*')
      .pipe(getStreamOutput('css', 'icon_font'));
}
exports.copyIcons = copyIcons;


/**
 * TASK: clean
 *    Empties the bin directory for a fresh population
 */
function clean() {
  return del(makeDestinationPath('**'), { force: true });
}
exports.clean = clean;


/**
 * TASK build
 *    The debug and production build task, which first clean the deployment
 *    by removing all existing files. Then the collection of common build
 *    tasks are run to produce a fresh destination build of the type indicated
 *    by the task being run
 */
const pre = gulp.series(clean, gulp.parallel(
  javascript,
  javascriptExternal,
  css,
  cssExternal,
  html,
  copyIcons,
  copyBowerComponents
));
exports.build = pre;
