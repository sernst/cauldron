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
   *
   * @param filename
   */
  function loadSourceFile(filename) {
    var noCache = '?nocache=' + exports.getNoCacheString();

    if (/.*\.css$/.test(filename)) {
      // Load Style sheet files
      return new Promise(function (resolve) {
        var link = document.createElement('link');
        link.rel = 'stylesheet';
        link.onload = resolve;
        link.href = filename + noCache;
        document.head.appendChild(link);
      });
    }

    if (/.*\.js$/.test(filename)) {
      // Load Javascript files
      return new Promise(function (resolve) {
        var script = document.createElement('script');
        script.onload = resolve;
        script.src = filename + noCache;
        document.head.appendChild(script);
      });
    }

    return Promise.reject();
  }

  /**
   * @param rootPath
   * @param filename
   */
  function loadDataFile(rootPath, filename) {
    var prom;

    if (window.RESULTS) {
      // If the results were included in the page directly, don't load them
      // again
      prom = Promise.resolve();
    } else {
      prom = loadSourceFile(rootPath + filename);
    }

    return prom
        .then(function () {
          exports.RESULTS = window.RESULTS;
          exports.DATA = window.RESULTS.data;
          exports.SETTINGS = window.RESULTS.settings;

          var proms = [];
          window.RESULTS.includes.forEach(function (includedFilename) {
            if (includedFilename.startsWith(':')) {
              includedFilename = includedFilename.slice(1);
            } else {
              includedFilename = rootPath + includedFilename;
            }
            proms.push(loadSourceFile(includedFilename));
          });

          return Promise.all(proms);
        })
        .then(function () {
          $('head').append(window.RESULTS.head);
          
          var body = $(window.RESULTS.body);
          body.find('[data-src]').each(function (index, e) {
            var element = $(e);
            var src = element.attr('data-src');
            if (src.startsWith('/')) {
              src = src.slice(1);
            }
            element.attr(
                'src',
                rootPath + '/' + src + '?nocache=' + exports.getNoCacheString()
            );
            element.attr('data-src', null);
          });
          
          $('.body-wrapper').html(body);
          $(window).trigger('resize');
          return exports.DATA;
        });
  }
  exports.loadDataFile = loadDataFile;

}());
