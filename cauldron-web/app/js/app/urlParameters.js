/* global $ */

const exports = window.CAULDRON || {};
window.CAULDRON = exports;


/**
 * Determines whether or not the specified test string represents a base 10
 * numeric value (either float or integer).
 *
 * @param testString
 * @returns {boolean}
 */
function isNumeric(testString) {
  if (!testString || /[^0-9.-]+/.test(testString)) {
    // Empty value or found illegal characters
    return false;
  }

  const decimalPoints = (testString.match(/\.+/g) || []).length;
  if (decimalPoints > 1) {
    // Numbers have at most one decimal point
    return false;
  }

  // Negative sign can only appear at the beginning of the number
  return testString.slice(1).indexOf('-') === -1;
}


/**
 * Parses the value portion of a url component variable into its numeric,
 * boolean or string value.
 *
 * @param value
 * @returns {*}
 */
function parseUrlValue(value) {
  if (isNumeric(value)) {
    return (value.indexOf('.') === -1)
      ? parseInt(value, 10)
      : parseFloat(value);
  }

  if (value.toLowerCase() === 'true') {
    return true;
  }

  if (value.toLowerCase() === 'false') {
    return false;
  }

  return decodeURIComponent(value);
}


/**
 * Parses the URL parameters from the current document URL and returns an
 * object with the key and value pairs for each entry. The values are parsed
 * into their actual numeric, boolean or decoded string values during parsing.
 *
 * @returns {object}
 */
function parseUrlParameters() {
  return document.location.search
    .replace(/(^\?)/, '')
    .split('&')
    .forEach(entry => entry.split('='))
    .filter(explodedEntry => (explodedEntry.length === 2))
    .reduce((result, [key, value]) => {
      const r = result;
      r[key] = parseUrlValue(value);
      return r;
    }, {});
}
exports.parseUrlParameters = parseUrlParameters;
