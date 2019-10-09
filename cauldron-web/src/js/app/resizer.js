import $ from 'jquery';

import utils from './utils';

let previousWidth = -100;
let resizePaused = false;

/**
 *
 * @param target
 */
function resizePlotlyBox(target) {
  const e = $(target);
  const parent = e.parent();
  const skip = e.parents('.cd-project-step-body').hasClass('closed');
  const parentV2 = e.parents('.cd-plotly-box-v2');

  if (skip || resizePaused) {
    // Do not resize plotly objects that are currently invisible
    return;
  }

  window.Plotly.relayout(e[0], {
    width: (parentV2 || parent).width(),
    height: (parentV2 || parent).height()
  });
}

/**
 *
 */
function resizePlotly() {
  if (!window.Plotly) {
    return;
  }

  $('.cd-plotly-box, .cd-plotly-box-v2').each((index, element) => {
    const e = $(element).find('.plotly-graph-div');
    resizePlotlyBox(e);
  });
}

/**
 * Function called when
 */
function onWindowResize() {
  const cauldron = utils.getRoot();
  if (!cauldron.RUNNING || resizePaused) {
    // Don't start resizing until everything has finished loading to prevent
    // race conditions during the load process of external libraries
    return;
  }

  const width = $(window).width();
  if (Math.abs(width - previousWidth) < 10) {
    return;
  }

  previousWidth = width;

  cauldron.resizeCallbacks.forEach((func) => func());
  resizePlotly();
}
window.onresize = onWindowResize;

/**
 *
 */
function pauseResizing() {
  resizePaused = true;
}

/**
 *
 */
function resumeResizing() {
  resizePaused = false;
  setTimeout(onWindowResize, 100);
}


export default {
  pauseResizing,
  resumeResizing,
  resizePlotly,
  resizePlotlyBox
};
