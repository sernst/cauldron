/* global $ */

const exports = window.CAULDRON || {};
window.CAULDRON = exports;

exports.RUNNING = false;


/**
 *
 */
function populateDom() {
  exports.addSnapshotBar();
  $('title').text(exports.TITLE);

  if (exports.SETTINGS.headerless) {
    // If no heading should be displayed skip creating one
    return;
  }

  exports.createHeader();
  $('.cd-body-header')
    .find('.project-title')
    .text(exports.TITLE);
}


/**
 *
 */
function start() {
  exports.RUNNING = true;

  // Resolve the ready promise
  exports.__on__.ready();

  $(window).resize();
}


/**
 * RUN APPLICATION
 */
$(() => {
  exports.PARAMS = exports.parseUrlParameters();
  exports.initialize()
    .then(populateDom)
    .then(start);
});
