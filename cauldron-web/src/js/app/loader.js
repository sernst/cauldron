import utils from './utils';

/**
 * @param include
 */
function loadSourceFile(include) {
  const cauldron = utils.getRoot();
  let filename;
  const noCache = `?nocache=${utils.getNoCacheString()}`;

  if (include.src.startsWith(':')) {
    filename = include.src.slice(1);
  } else {
    filename = cauldron.DATA_DIRECTORY + include.src;
  }

  const existing = window.document.getElementById(include.name);
  if (existing) {
    // If the source file is already loaded, don't load it again
    return Promise.resolve();
  }

  function onLoaded(resolve, element) {
    setTimeout(() => resolve(element), 250);
  }

  if (/.*\.css$/.test(filename)) {
    // Load Style sheet files
    return new Promise((resolve) => {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.onload = onLoaded.bind(null, resolve, link);
      link.href = filename + noCache;
      link.id = include.name;
      document.head.appendChild(link);
    });
  }

  if (/.*\.js$/.test(filename)) {
    // Load Javascript files
    return new Promise((resolve) => {
      const script = document.createElement('script');
      script.onload = onLoaded.bind(null, resolve, script);
      script.src = filename + noCache;
      script.id = include.name;
      document.head.appendChild(script);
    });
  }

  return Promise.reject();
}


/**
 *
 * @param includes
 * @returns {*}
 */
function loadSourceFiles(includes) {
  if (!includes) {
    return Promise.resolve([]);
  }

  return Promise.all(includes.map(loadSourceFile));
}


/**
 *
 */
function loadStepIncludes(steps) {
  if (!steps) {
    return Promise.resolve([]);
  }

  const proms = steps
    .filter((step) => step)
    .map((step) => loadSourceFiles(step.includes));

  return Promise.all(proms);
}

export default { loadSourceFile, loadSourceFiles, loadStepIncludes };
