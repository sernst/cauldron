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
   * @param filename
   */
  function loadDataFile(filename) {

    function loadComplete(resolve) {
      exports.DATA = window.RESULTS.data;
      exports.SETTINGS = window.RESULTS.settings;
      $('.body-wrapper').html(window.RESULTS.body);
      resolve(exports.DATA);
      $(window).trigger('resize');
    }

    if (window.RESULTS) {
      // If the results were included in the page directly, don't load them
      // again
      return new Promise(function (resolve) {
        loadComplete(resolve);
      });
    }

    return new Promise(function (resolve) {
      var script = document.createElement('script');
      script.onload = loadComplete.bind(null, resolve);
      script.src = filename;
      document.head.appendChild(script);
    });
  }
  exports.loadDataFile = loadDataFile;

}());

(function () {
  'use strict';

  var exports = window.CAULDRON || {};
  window.CAULDRON = exports;

  /**
   *
   * @param selector
   */
  function toggleVisible(selector) {
    $(selector).toggle();
  }
  exports.toggleVisible = toggleVisible;

  /**
   *
   * @param buttonId
   */
  function collapse(buttonId) {
    var btn = $('#' + buttonId);
    var open = btn.hasClass('closed');
    var items = btn.attr('data-' + (open ? 'opens' : 'closes'));
    var marks = btn.attr('data-marks-' + (open ? 'opened' : 'closed')) || '';

    marks = marks.split('|').map(function (selector) {
      return $(selector);
    });
    marks.push(btn);
    marks.forEach(function (target) {
      if (open) {
        target.removeClass('closed').addClass('opened');
      } else {
        target.removeClass('opened').addClass('closed');
      }
    });

    if (!items) {
      return;
    }

    items.split('|').forEach(function (target) {
      target = $(target);
      if (open) {
        target.show();
        btn.removeClass('closed');
      } else {
        target.hide();
        target.addClass('closed');
      }
    });

    $(window).resize();
  }
  exports.collapse = collapse;

  /**
   *
   * @param target
   * @param direction
   */
  function changeFontSize(target, direction) {
    target = $(target);
    var size = parseFloat(target.attr('data-font-size'));

    if (!direction) {
      size = parseFloat(target.attr('data-font-size-default'));
    } else {
      size = Math.max(0.1, size + direction * 0.1);
    }

    target.attr('data-font-size', size);
    target.css('font-size', size + 'em');
  }
  exports.changeFontSize = changeFontSize;

}());

(function () {
  'use strict';

  var exports = window.CAULDRON || {};
  window.CAULDRON = exports;


  /**
   * Function called when
   */
  function onWindowResize() {
    if (!exports.RUNNING) {
      // Don't start resizing until everything has finished loading to prevent
      // race conditions during the load process of external libraries
      return;
    }

    exports.resizeCallbacks.forEach(function (func) {
      func();
    });
    exports.resizePlotly();
  }
  window.onresize = onWindowResize;


  /**
   *
   */
  function resizePlotly() {
    $('.cd-plotly-box').each(function (index, element) {
      var e = $(element);
      var skip = e.parents('.cd-project-step-body').hasClass('closed');
      if (skip) {
        // Do not resize plotly objects that are currently invisible
        return;
      }

      Plotly.relayout(e.find('.plotly-graph-div')[0], {
        width: e.width(),
        height: e.height()
      });
      //Plotly.Plots.resize(e.find('.plotly-graph-div')[0]);
    });
  }
  exports.resizePlotly = resizePlotly;

}());
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
    
    return exports.loadDataFile(dataDirectory  +'/results.js')
      .then(function () {
        var title = exports.SETTINGS.title || exports.SETTINGS.id || id;
        var body = $('body');

        if (sid) {
          $('<div></div>')
              .addClass('snapshot-bar')
              .html('Snapshot: ' + exports.PARAMS['sid'])
              .prependTo(body);

          $('<div></div>')
              .addClass('snapshot-bar')
              .addClass('snapshot-bar-overlay')
              .html('Snapshot: ' + exports.PARAMS['sid'])
              .prependTo(body);

          title = '{' + sid + '} ' + title;
        }

        $('title').html(title);
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
          $(window).resize();
        });
  });

}());

