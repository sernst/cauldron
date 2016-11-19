/* global window */

const exports = window.CAULDRON || {};
window.CAULDRON = exports;


/**
 *
 */
function getNoCacheString() {
  const d = new Date();
  return [
    d.getUTCMilliseconds(),
    d.getUTCSeconds(),
    d.getUTCMinutes(),
    d.getUTCHours(),
    d.getUTCDay(),
    d.getUTCMonth(),
    d.getUTCFullYear()
  ].join('-');
}
exports.getNoCacheString = getNoCacheString;


/**
 *
 * @param lower
 * @returns {*|string|XML|void}
 */
function capitalize(lower) {
  return lower.replace(/(?:^|\s)\S/g, a => a.toUpperCase());
}
exports.capitalize = capitalize;


/**
 *
 * @param value
 * @param unc
 * @returns {string}
 */
function toDisplayNumber(value, unc) {
  function toDisplayValue(v) {
    return (0.01 * Math.round(100.0 * v)).toFixed(2);
  }

  return `${toDisplayValue(value)} &#177; ${toDisplayValue(unc)}`;
}
exports.toDisplayNumber = toDisplayNumber;
