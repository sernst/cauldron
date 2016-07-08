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