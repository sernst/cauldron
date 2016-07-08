(function () {
  'use strict';

  var exports = window.CAULDRON || {};
  window.CAULDRON = exports;

  exports.resizeCallbacks = [];

  /**
   *
   */
  function getNoCacheString() {
    var d = new Date();
    return d.getUTCMilliseconds() + '-' +
        d.getUTCSeconds() + '-' +
        d.getUTCMinutes() + '-' +
        d.getUTCHours() + '-' +
        d.getUTCDay() + '-' +
        d.getUTCMonth() + '-' +
        d.getUTCFullYear();
  }
  exports.getNoCacheString = getNoCacheString;


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
   * @param lower
   * @returns {*|string|XML|void}
   */
  function capitalize(lower) {
    return (lower ? this.toLowerCase() : this)
      .replace(/(?:^|\s)\S/g, function(a) {
        return a.toUpperCase();
      });
  }
  exports.capitalize = capitalize;


  /**
   *
   * @param value
   * @param unc
   * @returns {string}
   */
  function toDisplayNumber(value, unc) {
    return (0.01*Math.round(100.0*value)).toFixed(2) +
      ' &#177; ' +
      (0.01*Math.round(100.0*unc)).toFixed(2);
  }
  exports.toDisplayNumber = toDisplayNumber;


  /**
   * @param include
   */
  function loadSourceFile(include) {
    var filename;
    var noCache = '?nocache=' + exports.getNoCacheString();

    if (include.src.startsWith(':')) {
      filename = include.src.slice(1);
    } else {
      filename = exports.DATA_DIRECTORY + include.src;
    }

    if ($('#' + include.name).length > 0) {
      // If the source file is already loaded, don't load it again
      return Promise.resolve();
    }

    if (/.*\.css$/.test(filename)) {
      // Load Style sheet files
      return new Promise(function (resolve) {
        var link = document.createElement('link');
        link.rel = 'stylesheet';
        link.onload = resolve;
        link.href = filename + noCache;
        link.id = include.name;
        document.head.appendChild(link);
      });
    }

    if (/.*\.js$/.test(filename)) {
      // Load Javascript files
      return new Promise(function (resolve) {
        var script = document.createElement('script');
        script.onload = resolve;
        script.src = filename + noCache;
        script.id = include.name;
        document.head.appendChild(script);
      });
    }

    return Promise.reject();
  }


  /**
   *
   * @param includes
   * @returns {*}
   */
  function loadSourceFiles(includes) {
    if (!includes) {
      return Promise.resolve();
    }

    var proms = [];
    includes.forEach(function (include) {
      proms.push(loadSourceFile(include));
    });

    return Promise.all(proms);
  }
  exports.loadSourceFiles = loadSourceFiles;


  /**
   *
   */
  function loadDataFile() {
    var prom;

    if (window.RESULTS) {
      // If the results were included in the page directly, don't load them
      // again
      prom = Promise.resolve();
    } else {
      prom = loadSourceFile({
        name: 'cauldron-project',
        src: '/results.js'
      });
    }

    return prom
        .then(function () {
          exports.RESULTS = window.RESULTS;
          exports.DATA = window.RESULTS.data;
          exports.SETTINGS = window.RESULTS.settings;
          return exports.loadSourceFiles(window.RESULTS.includes);
        })
        .then(function () {
          // Load the include files for each step

          var proms = [];
          exports.RESULTS.steps.forEach(function (step) {
            proms.push(exports.loadSourceFiles(step.includes))
          });

          return Promise.all(proms);
        })
        .then(function () {
          var head = $('head');
          var body = $('.body-wrapper');

          window.RESULTS.steps.forEach(function (step) {
            if (step.head) {
              head.append(step.head);
            }

            if (!step.body) {
              return;
            }

            var stepBody = $(step.body);
            stepBody.find('[data-src]').each(function (index, e) {
              var element = $(e);
              var src = element.attr('data-src');

              if (src.startsWith('/')) {
                src = src.slice(1);
              }

              element.attr(
                  'src',
                  exports.DATA_DIRECTORY + '/' + src +
                    '?nocache=' + exports.getNoCacheString()
              );
              element.attr('data-src', null);
            });

            body.append(stepBody);
          });

          $(window).trigger('resize');
          return exports.DATA;
        });
  }
  exports.loadDataFile = loadDataFile;

}());
