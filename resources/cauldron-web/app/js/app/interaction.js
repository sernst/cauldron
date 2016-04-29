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


}());
