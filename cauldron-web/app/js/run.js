(function () {
  'use strict';

  var exports = window.CAULDRON || {};
  window.CAULDRON = exports;

  exports.RUNNING = false;


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
    return exports.initialize()
        .then(function () {
          var body = $('body');
  
          exports.addSnapshotBar();
          $('title').text(exports.TITLE);

          if (exports.SETTINGS.headerless) {
            return;
          }

          exports.createHeader();
          $('.cd-body-header').find('.project-title').text(exports.TITLE);
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
          exports.RUNNING = true;

          // Resolve the ready promise
          exports.__on__.ready();

          $(window).resize();
        });
  });

}());

