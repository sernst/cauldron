/* global $ */

const exports = window.CAULDRON || {};
window.CAULDRON = exports;

let selectedStep;
let selectionTimeout;
let processingPromise;


/**
 *
 * @param stepDom
 */
function setSelected(stepDom) {
  if (!stepDom || stepDom.hasClass('cd-project-step--selected')) {
    return;
  }

  stepDom.addClass('cd-project-step--selected');

  const header = stepDom.find('.cd-project-step__header');

  header
    .addClass('cd-project-step__header--selected')
    .removeClass(header.attr('data-default-modifier'));
}

/**
 *
 * @param stepDom
 */
function removeSelected(stepDom) {
  stepDom.removeClass('cd-project-step--selected');

  const header = stepDom.find('.cd-project-step__header');
  header
    .removeClass('cd-project-step__header--selected')
    .addClass(header.attr('data-default-modifier'));
}


/**
 *
 */
function doSelectionUpdate() {
  const step = selectedStep;
  selectionTimeout = null;

  if (!step) {
    return;
  }

  $('.body-wrapper')
    .find('.cd-project-step')
    .each((index, e) => {
      const stepDom = $(e);
      const name = stepDom.attr('data-step-name');
      if (name === step.name) {
        setSelected(stepDom);
      } else {
        removeSelected(stepDom);
      }
    });
}


/**
 *
 * @param step
 * @return {Promise}
 */
function updateSelectedStep(step) {
  if (step) {
    selectedStep = step;
  }

  if (selectionTimeout) {
    return Promise.resolve(selectedStep);
  }

  return new Promise((resolve) => {
    function onTimeout() {
      doSelectionUpdate();
      resolve(selectedStep);
    }

    selectionTimeout = setTimeout(onTimeout, 10);
  });
}
exports.updateSelectedStep = updateSelectedStep;


/**
 *
 * @param step
 * @returns {*}
 */
function prepareStepBody(step) {
  if (!step || !step.body) {
    return null;
  }

  const stepBody = $(step.body);

  function getSrc(targetElement) {
    const result = targetElement.attr('data-src');
    return (result && result.startsWith('/')) ? result.slice(1) : result;
  }

  stepBody.find('[data-src]').each((index, e) => {
    const element = $(e);
    const src = getSrc(element);

    element.attr(
      'src',
      `${exports.DATA_DIRECTORY}/${src}?nocache=${exports.getNoCacheString()}`
    );
    element.attr('data-src', null);
  });

  return stepBody;
}
exports.prepareStepBody = prepareStepBody;


function onReadyToProcess(updates) {
  // Add the body for each step to the page body
  const body = $('.body-wrapper');
  let before;

  updates.forEach((update) => {
    const existing = $(`[data-step-name="${update.name}"]`);

    if (update.action === 'removed') {
      existing.remove();
      return;
    }

    let stepDom = exports.prepareStepBody(update.step);
    if (selectedStep && update.name === selectedStep.name) {
      setSelected(stepDom);
    }

    if (update.action === 'updated') {
      existing.replaceWith(stepDom);
      return;
    }

    if (update.action === 'modified') {
      stepDom = body.find(`[data-step-name="${update.name}"]`);
      stepDom.find('.cd-step-title').html(update.title || update.name);
      stepDom.detach();
    }

    // Modified or added steps get inserted into the dom
    if (update.after) {
      before = body.find(`[data-step-name="${update.after}"]`);
    } else {
      before = body.find('.cd-body-header').after(stepDom);
    }

    if (before && before.length > 0) {
      before.after(stepDom);
    } else if (update.after) {
      body.append(stepDom);
    } else {
      body.prepend(stepDom);
    }
  });

  $(window).trigger('resize');

  exports.updateSelectedStep();
}


/**
 *
 */
function processStepUpdates(updates, stepToSelect) {
  if (!updates) {
    return Promise.resolve();
  }

  if (!processingPromise) {
    processingPromise = window.CD.on.ready;
  }

  if (stepToSelect) {
    selectedStep = stepToSelect;
  }

  const steps = updates.map(update => update.step);

  processingPromise = processingPromise
    .then(() => exports.loadStepIncludes(steps))
    .then(() => onReadyToProcess(updates));
  return processingPromise;
}
exports.processStepUpdates = processStepUpdates;
