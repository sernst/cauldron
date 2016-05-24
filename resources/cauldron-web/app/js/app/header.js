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
    var buttons = header.find('.buttons');
  }
  exports.createHeader = createHeader;
  
}());