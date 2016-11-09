const exports = window.CAULDRON || {};
window.CAULDRON = exports;

/**
 * @param include
 */
function loadSourceFile(include) {
  let filename;
  const noCache = `?nocache=${exports.getNoCacheString()}`;

  if (include.src.startsWith(':')) {
    filename = include.src.slice(1);
  } else {
    filename = exports.DATA_DIRECTORY + include.src;
  }

  const existing = window.document.getElementById(include.name);
  if (existing) {
    // If the source file is already loaded, don't load it again
    return Promise.resolve();
  }

  if (/.*\.css$/.test(filename)) {
    // Load Style sheet files
    return new Promise(function (resolve) {
      var link = document.createElement('link');
      link.rel = 'stylesheet';
      link.onload = resolve;
      link.href = filename + noCache;
      link.id = include.name;
      document.head.appendChild(link);
    });
  }

  if (/.*\.js$/.test(filename)) {
    // Load Javascript files
    return new Promise(function (resolve) {
      var script = document.createElement('script');
      script.onload = resolve;
      script.src = filename + noCache;
      script.id = include.name;
      document.head.appendChild(script);
    });
  }

  return Promise.reject();
}
exports.loadSourceFile = loadSourceFile;


/**
 *
 * @param includes
 * @returns {*}
 */
function loadSourceFiles(includes) {
  if (!includes) {
    return Promise.resolve([]);
  }

  var proms = [];
  includes.forEach(function (include) {
    proms.push(exports.loadSourceFile(include));
  });

  return Promise.all(proms);
}
exports.loadSourceFiles = loadSourceFiles;


/**
 *
 */
function loadStepIncludes(steps) {
  if (!steps) {
    return Promise.resolve([]);
  }

  var proms = [];
  steps.forEach(function (step) {
    if (!step) {
      return;
    }

    proms.push(exports.loadSourceFiles(step.includes))
  });

  return Promise.all(proms);
}
exports.loadStepIncludes = loadStepIncludes;
