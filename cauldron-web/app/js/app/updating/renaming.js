/* global $ */

const exports = window.CAULDRON || {};
window.CAULDRON = exports;


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
 * Renames steps. This is carried out in a two-step process to prevent
 * collisions between shared old names and new names among different steps.
 *
 * @param renames
 */
function processStepRenames(renames) {
  if (!renames) {
    return Promise.resolve(renames);
  }

  const body = $('.body-wrapper');

  Object.keys(renames).forEach(
    (oldName) => addRenameAttribute(body, renames, oldName)
  );

  body.find('[data-step-rename]').each((i, element) => renameStep(element));

  return Promise.resolve(renames);
}
exports.processStepRenames = processStepRenames;
