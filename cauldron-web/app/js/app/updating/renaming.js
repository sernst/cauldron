/* global $ */

const exports = window.CAULDRON || {};
window.CAULDRON = exports;

let processingPromise;


/**
 *
 * @param body
 * @param renames
 * @param oldName
 */
function addRenameAttribute(body, renames, oldName) {
  const data = renames[oldName];
  const stepBody = body.find(`[data-step-name="${oldName}"]`);

  stepBody.attr('data-step-rename', data.name);
  stepBody.find('.cd-step-title').html(data.title || data.name);
}


function renameStep(element) {
  const e = $(element);
  const newName = e.attr('data-step-rename');

  e.attr('data-step-rename', null)
      .attr('data-step-name', newName)
    .find('.step-anchor')
      .each((i, anchor) => {
        const a = $(anchor);
        a.attr('name', `${newName}${a.attr('data-type')}`);
      });
}


/**
 *
 * @param renames
 * @returns {Promise.<T>}
 */
function onProcessingReady(renames) {
  const body = $('.body-wrapper');

  Object.keys(renames).forEach(
    (oldName) => addRenameAttribute(body, renames, oldName)
  );

  body.find('[data-step-rename]').each((i, element) => renameStep(element));

  return Promise.resolve(renames);
}


/**
 * Renames steps. This is carried out in a two-step process to prevent
 * collisions between shared old names and new names among different steps.
 *
 * @param renames
 */
function processStepRenames(renames) {
  if (!renames) {
    return Promise.resolve(renames);
  }

  if (!processingPromise) {
    processingPromise = window.CD.on.ready;
  }

  processingPromise = processingPromise
    .then(() => onProcessingReady(renames));
  return processingPromise;
}
exports.processStepRenames = processStepRenames;
