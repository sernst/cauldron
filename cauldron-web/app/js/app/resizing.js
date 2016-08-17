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