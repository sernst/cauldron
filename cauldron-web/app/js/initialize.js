(function () {
  'use strict';

  var exports = window.CAULDRON || {};
  window.CAULDRON = exports;

  exports.resizeCallbacks = [];


  /**
   * A fake require function that is needed for the inclusion of some
   * elements within the DOM (e.g. plotly offline)
   *
   * @param preloaders
   * @param callback
   */
  function fakeRequire(preloaders, callback) {
    var callers = [];
    preloaders.forEach(function (entry) {
      if (entry === 'plotly') {
        callers.push(window.Plotly);
      }
    });
    callback.apply(this, callers);
  }
  window.require = fakeRequire;


  /**
   *
   * @returns {*}
   */
  function initializeDataDirectory() {
    var dataDirectory = window.PROJECT_DIRECTORY;
    var id = exports.PARAMS['id'];
    var sid = exports.PARAMS['sid'];

    if (!dataDirectory) {
      dataDirectory = 'reports/' + id;
      if (sid) {
        dataDirectory += '/snapshots/' + sid;
      } else {
        dataDirectory += '/latest';
      }
    }

    exports.DATA_DIRECTORY = dataDirectory;
    return dataDirectory;
  }


  /**
   *
   * @returns {boolean}
   */
  function addSnapshotBar() {
    var sid = exports.PARAMS['sid'];
    var body = $('body');

    if (!sid) {
      return false;
    }

    $('<div></div>')
        .addClass('snapshot-bar')
        .text('Snapshot: ' + exports.PARAMS['sid'])
        .prependTo(body);

    $('<div></div>')
        .addClass('snapshot-bar')
        .addClass('snapshot-bar-overlay')
        .text('Snapshot: ' + exports.PARAMS['sid'])
        .prependTo(body);

      exports.TITLE = '{' + sid + '} ' + exports.TITLE;
  }
  exports.addSnapshotBar = addSnapshotBar;


  /**
   *
   */
  function initialize() {
    var prom;

    initializeDataDirectory();

    if (window.RESULTS) {
      // If the results were included in the page directly, don't load them
      // again
      prom = Promise.resolve();
    } else if (window.RESULTS_FILENAME) {
      prom = exports.loadSourceFile({
        name: 'cauldron-project',
        src: ':' + window.RESULTS_FILENAME
      });
    } else {
      prom = exports.loadSourceFile({
        name: 'cauldron-project',
        src: '/results.js'
      });
    }

    return prom
        .then(function () {
          exports.RESULTS = window.RESULTS;
          exports.DATA = window.RESULTS.data;
          exports.SETTINGS = window.RESULTS.settings;
          exports.TITLE = exports.SETTINGS.title || exports.SETTINGS.id || id;
          return exports.loadSourceFiles(window.RESULTS.includes);
        })
        .then(function () {
          // Load the include files for each step
          return exports.loadStepIncludes(exports.RESULTS.steps);
        })
        .then(function () {
          // Add the body for each step to the page body
          var body = $('.body-wrapper');

          window.RESULTS.steps.forEach(function (step) {
            var stepBody = exports.prepareStepBody(step);
            if (stepBody) {
              body.append(stepBody);
            }
          });

          $(window).trigger('resize');
          return exports.DATA;
        });
  }
  exports.initialize = initialize;

}());
