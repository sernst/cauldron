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


/**
 *
 * @param lower
 * @returns {*|string|void}
 */
function capitalize(lower) {
  return lower.replace(/(?:^|\s)\S/g, (a) => a.toUpperCase());
}

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

/**
 *
 * @returns {*|{}}
 */
function getRoot() {
  window.CAULDRON = window.CAULDRON || {};
  return window.CAULDRON;
}

export default {
  getNoCacheString,
  toDisplayNumber,
  capitalize,
  getRoot
};
