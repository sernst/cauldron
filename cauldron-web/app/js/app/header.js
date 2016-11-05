/* global $ */

const exports = window.CAULDRON || {};
window.CAULDRON = exports;

const headerDom = [
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
  const header = $(headerDom.join(''))
      .prependTo($('.body-wrapper'));

  if (exports.RESULTS.has_error) {
    header.addClass('project-error');
  }
}
exports.createHeader = createHeader;
