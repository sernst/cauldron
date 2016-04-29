(function () {
  'use strict';

  var exports = window.CAULDRON || {};
  window.CAULDRON = exports;

  /**
   * Function called when
   */
  function onWindowResize() {
    exports.resizeCallbacks.forEach(function (func) {
      func();
    });
  }
  window.onresize = onWindowResize;

}());