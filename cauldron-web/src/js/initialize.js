import $ from 'jquery';

import utils from './app/utils';
import header from './app/header';
import loader from './app/loader';
import updates from './app/updating/updates';

/**
 *
 * @returns {*}
 */
function getDataDirectory() {
  const cauldron = utils.getRoot();

  if (window.PROJECT_DIRECTORY) {
    return window.PROJECT_DIRECTORY;
  }

  if (cauldron.PARAMS.data_root) {
    return cauldron.PARAMS.data_root;
  }

  const id = cauldron.PARAMS.id || window.PROJECT_ID;
  const { sid } = cauldron.PARAMS;

  const dataDirectory = [
    'reports',
    id || '',
    sid ? 'snapshots' : 'latest',
    sid || ''
  ];

  return dataDirectory
    .filter((folder) => folder.length > 0)
    .join('/');
}


/**
 *
 * @returns {boolean}
 */
function addSnapshotBar() {
  const cauldron = utils.getRoot();
  const { sid } = cauldron.PARAMS;
  const body = $('body');

  if (!sid) {
    return false;
  }

  $('<div></div>')
    .addClass('snapshot-bar')
    .text(`Snapshot: ${sid}`)
    .prependTo(body);

  $('<div></div>')
    .addClass('snapshot-bar')
    .addClass('snapshot-bar-overlay')
    .text(`Snapshot: ${cauldron.PARAMS.sid}`)
    .prependTo(body);

  cauldron.TITLE = `{${sid}} ${cauldron.TITLE}`;
  return true;
}

/**
 *
 * @returns {*}
 */
function loadProjectData() {
  if (window.RESULTS) {
    // If the results are already available abort the load process
    return Promise.resolve();
  }

  if (window.RESULTS_FILENAME) {
    return loader.loadSourceFile({
      name: 'cauldron-project',
      src: `:${window.RESULTS_FILENAME}`
    });
  }

  return loader.loadSourceFile({
    name: 'cauldron-project',
    src: '/results.js'
  });
}

function loadIncludes() {
  const cauldron = utils.getRoot();

  if (window.COMBINED_INCLUDES) {
    return loader.loadSourceFiles(window.COMBINED_INCLUDES);
  }

  return loader.loadSourceFiles(window.RESULTS.includes)
    .then(() => loader.loadStepIncludes(cauldron.RESULTS.steps));
}

function preload() {
  const cauldron = utils.getRoot();
  if (!cauldron.PARAMS.preload_url) {
    return Promise.resolve();
  }

  return Promise.resolve();
}

/**
 *
 */
function populateDom() {
  const cauldron = utils.getRoot();
  addSnapshotBar();

  $('title').text(cauldron.TITLE);

  if (cauldron.SETTINGS.headerless) {
    // If no heading should be displayed skip creating one
    return;
  }

  header.createHeader();
  $('.cd-body-header')
    .find('.project-title')
    .text(cauldron.TITLE);
}

/**
 *
 */
function initialize() {
  const cauldron = utils.getRoot();

  cauldron.DATA_DIRECTORY = getDataDirectory();
  return preload()
    .then(() => loadProjectData())
    .then(() => {
      window.CAULDRON_VERSION = window.RESULTS.cauldron_version;

      cauldron.RESULTS = window.RESULTS;
      cauldron.DATA = window.RESULTS.data;
      cauldron.SETTINGS = window.RESULTS.settings;
      cauldron.TITLE = cauldron.SETTINGS.title || cauldron.SETTINGS.id;
      return loadIncludes();
    })
    .then(() => {
      // Add the body for each step to the page body
      const body = $('.body-wrapper');

      window.RESULTS.steps.forEach((step) => {
        const stepBody = updates.prepareStepBody(step);
        if (stepBody) {
          body.append(stepBody);
        }
      });

      $(window).trigger('resize');
      return cauldron.DATA;
    })
    .then(populateDom);
}

export default { initialize };
