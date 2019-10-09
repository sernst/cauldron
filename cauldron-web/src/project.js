import $ from 'jquery';
import d3 from 'd3/dist/d3.min';
import Handsontable from 'handsontable';
import katex from 'katex';
import jstree from 'jstree';

import initializer from './js/initialize';
import utils from './js/app/utils';
import parser from './js/app/parser';
import interaction from './js/app/interaction';
import renaming from './js/app/updating/renaming';
import updates from './js/app/updating/updates';
import resizer from './js/app/resizer';

import './project.scss';

// Global includes
window.$ = $;
window.d3 = d3;
window.Handsontable = Handsontable;
window.katex = katex;
window.jstree = jstree;

/**
 * A fake require function that is needed for the inclusion of some
 * elements within the DOM (e.g. plotly offline)
 *
 * @param preloaders
 * @param callback
 */
function fakeRequire(preloaders, callback) {
  const callers = [];
  preloaders.forEach((entry) => {
    if (entry === 'plotly') {
      callers.push(window.Plotly);
    }
  });

  callback.apply(this, callers);
}
window.require = fakeRequire;

/**
 *
 */
function start() {
  const cauldron = utils.getRoot();
  cauldron.RUNNING = true;

  // Resolve the ready promise
  // eslint-disable-next-line no-underscore-dangle
  cauldron.__on__.ready();
  $(window).resize();
}

/**
 * RUN APPLICATION
 */
$(() => {
  const cauldron = utils.getRoot();
  cauldron.RUNNING = false;
  cauldron.SETTINGS = {};
  cauldron.notebookVersion = 1;
  cauldron.resizeCallbacks = [];
  cauldron.PARAMS = parser.parseUrlParameters();

  // Public functions that can be called from external JS sources.
  cauldron.capitalize = utils.capitalize;
  cauldron.getNoCacheString = utils.getNoCacheString;
  cauldron.toDisplayNumber = utils.toDisplayNumber;
  cauldron.scrollToAnchor = interaction.scrollToAnchor;
  cauldron.changeFontSize = interaction.changeFontSize;
  cauldron.collapse = interaction.collapse;
  cauldron.toggleVisible = interaction.toggleVisible;
  cauldron.processStepRenames = renaming.processStepRenames;
  cauldron.prepareStepBody = updates.prepareStepBody;
  cauldron.processStepUpdates = updates.processStepUpdates;
  cauldron.updateSelectedStep = updates.updateSelectedStep;
  cauldron.pauseResizing = resizer.pauseResizing;
  cauldron.resumeResizing = resizer.resumeResizing;
  cauldron.resizePlotly = resizer.resizePlotly;
  cauldron.resizePlotlyBox = resizer.resizePlotlyBox;

  return initializer.initialize().then(start);
});
