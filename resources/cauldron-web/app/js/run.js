(function () {
  'use strict';

  var exports = window.CAULDRON || {};
  window.CAULDRON = exports;



  /**
   *
   */
  function parseUrlParameters() {
    var out = {};

    document.location.search
      .replace(/(^\?)/, '')
      .split("&")
      .forEach(function (item) {
        item = item.split("=");
        if (item.length < 2) {
          return;
        }

        var v = item[1];
        if (!/[^0-9\.]+/.test(v)) {
          if (v.indexOf('.') === -1) {
            v = parseInt(v, 10);
          } else {
            v = parseFloat(v);
          }
        } else if (v.toLowerCase() === 'true') {
          v = true;
        } else if (v.toLowerCase() === 'false') {
          v = false;
        } else {
          v = decodeURIComponent(v);
        }

        out[item[0]] = v;
      });
    return out;
  }
  exports.parseUrlParameters = parseUrlParameters;

  /**
   *
   */
  function run() {
    var dataFilename = window.RESULTS_FILENAME || 
        ('reports/' + exports.PARAMS['id'] + '/results.js');
    
    return exports.loadDataFile(dataFilename)
      .then(function () {
        $('title').html(
            exports.SETTINGS.title ||
            exports.SETTINGS.id ||
            'Cauldron'
        );
      });
  }
  exports.run = run;

  /**
   * RUN APPLICATION
   */
  $(function () {
    exports.PARAMS = exports.parseUrlParameters();

    exports.run()
      .then(function () {
        // Add auto resizing to plotly graphs
        exports.resizeCallbacks.push(function () {
          $('.plotly-graph-div').each(function (index, e) {
            if ($(e).parents('.cd-project-step').hasClass('collapsed')) {
              console.log('skipped:', index, e);
              // Do not resize plotly objects that are currently invisible
              return;
            }

            Plotly.Plots.resize(e);
          });
        });
      });
  });

}());

