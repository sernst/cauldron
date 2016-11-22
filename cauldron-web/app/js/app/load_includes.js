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
    return new Promise((resolve) => {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.onload = (() => resolve(link));
      link.href = filename + noCache;
      link.id = include.name;
      document.head.appendChild(link);
    });
  }

  if (/.*\.js$/.test(filename)) {
    // Load Javascript files
    return new Promise((resolve) => {
      const script = document.createElement('script');
      script.onload = (() => resolve(script));
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

  const proms = includes.map(include => exports.loadSourceFile(include));
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

  const proms = steps
    .filter(step => step)
    .map(step => exports.loadSourceFiles(step.includes));

  return Promise.all(proms);
}
exports.loadStepIncludes = loadStepIncludes;
