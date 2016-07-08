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
   */
  function initialize() {
    var prom;

    initializeDataDirectory();

    if (window.RESULTS) {
      // If the results were included in the page directly, don't load them
      // again
      prom = Promise.resolve();
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

(function () {
  'use strict';

  var exports = window.CAULDRON || {};
  window.CAULDRON = exports;

  var headerDom = [
    '<div class="cd-body-header">',
    '<div class="menu-icon"></div>',
    '<div class="project-title"></div>',
    '<div class="spacer"></div>',
    '<div class="buttons"></div>',
    '</div>'
  ];

  /**
   *
   */
  function createHeader() {
    var header = $(headerDom.join(''))
        .prependTo($('.body-wrapper'));
    if (exports.RESULTS.has_error) {
      header.addClass('project-error');
    }
    var buttons = header.find('.buttons');
  }
  exports.createHeader = createHeader;
  
}());
(function () {
  'use strict';

  var exports = window.CAULDRON || {};
  window.CAULDRON = exports;


  /**
   *
   * @param name
   */
  function scrollToAnchor(name){
    var aTag = $("a[name='"+ name +"']");
    $('html,body').animate({scrollTop: aTag.offset().top}, 'slow');
  }
  exports.scrollToAnchor = scrollToAnchor;


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
      $(window).resize();
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


    var existing = window.document.getElementById(include.name);
    if (existing) {
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
  exports.loadSourceFile = loadSourceFile;


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
      proms.push(exports.loadSourceFile(include));
    });

    return Promise.all(proms);
  }
  exports.loadSourceFiles = loadSourceFiles;


  /**
   *
   */
  function loadStepIncludes(steps) {
    var proms = [];
    steps.forEach(function (step) {
      if (!step) {
        return;
      }

      proms.push(exports.loadSourceFiles(step.includes))
    });

    return Promise.all(proms);
  }
  exports.loadStepIncludes = loadStepIncludes;


}());
(function () {
  'use strict';

  var exports = window.CAULDRON || {};
  window.CAULDRON = exports;

  var previousWidth = -100;

  /**
   * Function called when
   */
  function onWindowResize() {
    if (!exports.RUNNING) {
      // Don't start resizing until everything has finished loading to prevent
      // race conditions during the load process of external libraries
      return;
    }

    var width = $(window).width();
    if (Math.abs(width - previousWidth) < 10) {
      return;
    }

    previousWidth = width;

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


  /**
   *
   * @param step
   * @returns {*}
   */
  function prepareStepBody(step) {
    if (!step || !step.body) {
      return null;
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

    return stepBody;
  }
  exports.prepareStepBody = prepareStepBody;


  /**
   *
   */
  function processStepUpdates(updates) {
    console.log('UPDATES:', updates);
    if (!updates) {
      return;
    }

    var steps = updates.map(function(update) {
      return update.step;
    });

    return exports.loadStepIncludes(steps)
        .then(function () {
          // Add the body for each step to the page body
          var body = $('.body-wrapper');

          updates.forEach(function (update) {
            var existing = $('[data-step-name="' + update.name + '"]');
            if (update.action === 'removed') {
              existing.remove();
              return;
            }

            var stepBody = exports.prepareStepBody(update.step);

            if (update.action === 'updated') {
              existing.replaceWith(stepBody);
              return;
            }

            if (update.action === 'modified') {
              stepBody = body.find('[data-step-name="' + update.name + '"]');
              stepBody.attr('data-step-name', update.new_name);
              stepBody.find('.cd-step-title').html(
                  update.title || update.new_name
              );
              stepBody.detach();
            }

            // Modified or added steps get inserted into the dom
            var after = update.after;
            if (!after) {
              body.prepend(stepBody);
            } else {
              body.find('[data-step-name="' + after + '"]')
                  .after(stepBody);
            }
          });

          $(window).trigger('resize');
        });
  }
  exports.processStepUpdates = processStepUpdates;

}());
(function () {
  'use strict';

  var exports = window.CAULDRON || {};
  window.CAULDRON = exports;


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
    return exports.initialize()
        .then(function () {
          var title = exports.SETTINGS.title || exports.SETTINGS.id || id;
          var body = $('body');
  
          if (exports.PARAMS['sid']) {
            $('<div></div>')
                .addClass('snapshot-bar')
                .text('Snapshot: ' + exports.PARAMS['sid'])
                .prependTo(body);
  
            $('<div></div>')
                .addClass('snapshot-bar')
                .addClass('snapshot-bar-overlay')
                .text('Snapshot: ' + exports.PARAMS['sid'])
                .prependTo(body);
  
            title = '{' + sid + '} ' + title;
          }
  
          $('title').text(title);

          if (exports.SETTINGS.headerless) {
            return;
          }

          exports.createHeader();
          $('.cd-body-header').find('.project-title').text(title);
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

