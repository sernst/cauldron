/* global $ */
/* global window */

const exports = window.CAULDRON || {};
window.CAULDRON = exports;

let previousWidth = -100;

/**
 * Function called when
 */
function onWindowResize() {
  if (!exports.RUNNING) {
    // Don't start resizing until everything has finished loading to prevent
    // race conditions during the load process of external libraries
    return;
  }

  const width = $(window).width();
  if (Math.abs(width - previousWidth) < 10) {
    return;
  }

  previousWidth = width;

  exports.resizeCallbacks.forEach(func => func());
  exports.resizePlotly();
}
window.onresize = onWindowResize;


/**
 *
 */
function resizePlotly() {
  if (!window.Plotly) {
    return;
  }

  $('.cd-plotly-box').each((index, element) => {
    const e = $(element);
    const skip = e.parents('.cd-project-step-body').hasClass('closed');
    if (skip) {
      // Do not resize plotly objects that are currently invisible
      return;
    }

    window.Plotly.relayout(e.find('.plotly-graph-div')[0], {
      width: e.width(),
      height: e.height()
    });
  });
}
exports.resizePlotly = resizePlotly;
