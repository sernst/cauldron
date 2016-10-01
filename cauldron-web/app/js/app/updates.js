(function () {
  'use strict';

  var exports = window.CAULDRON || {};
  window.CAULDRON = exports;

  var selectedStep;
  var selectionTimeout;

  function setSelected(stepDom) {
    if (!stepDom || stepDom.hasClass('cd-project-step--selected')) {
      return;
    }

    stepDom.addClass('cd-project-step--selected');

    var header = stepDom.find('.cd-project-step__header');
    header
      .addClass('cd-project-step__header--selected')
      .removeClass(header.attr('data-default-modifier'));
  }

  function removeSelected(stepDom) {
    stepDom.removeClass('cd-project-step--selected');

    var header = stepDom.find('.cd-project-step__header');
    header
      .removeClass('cd-project-step__header--selected')
      .addClass(header.attr('data-default-modifier'));
  }

  /**
   *
   */
  function doSelectionUpdate() {
    var step = selectedStep;
    selectionTimeout = null;

    if (!step) {
      return null;
    }

    console.log('SELECTED:', step);

    $('.body-wrapper')
      .find('.cd-project-step')
      .each(function (index, e) {
        var stepDom = $(e);
        var name = stepDom.attr('data-step-name');
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

    console.log('UPDATING SELECTED:', selectedStep);

    if (selectionTimeout) {
      return Promise.resolve(selectedStep);
    }

    return new Promise(function (resolve) {
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

    var stepBody = $(step.body);

    stepBody.find('[data-src]').each(function (index, e) {
      var element = $(e);
      var src = element.attr('data-src');

      if (src.startsWith('/')) {
        src = src.slice(1);
      }

      element.attr(
          'src',
          exports.DATA_DIRECTORY + '/' + src +
          '?nocache=' + exports.getNoCacheString()
      );
      element.attr('data-src', null);
    });

    return stepBody;
  }
  exports.prepareStepBody = prepareStepBody;


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

    var body = $('.body-wrapper');

    // Add rename attributes
    Object.keys(renames).forEach(function (oldName) {
      var data = renames[oldName];
      var stepBody = body.find('[data-step-name="' + oldName + '"]');
      stepBody.attr('data-step-rename', data.name);
      stepBody.find('.cd-step-title').html(data.title || data.name);
    });

    // Process rename attributes
    body.find('[data-step-rename]').each(function (index, element) {
      var e = $(element);
      var newName = e.attr('data-step-rename');

      e.attr('data-step-rename', null);
      e.attr('data-step-name', newName);
      e.find('.step-anchor').attr('name', newName);
    });

    return Promise.resolve(renames);
  }
  exports.processStepRenames = processStepRenames;


  /**
   *
   */
  function processStepUpdates(updates, stepToSelect) {
    if (!updates) {
      return;
    }

    if (stepToSelect) {
      selectedStep = stepToSelect;
    }

    var steps = updates.map(function(update) {
      return update.step;
    });

    return exports.loadStepIncludes(steps)
      .then(function () {
        // Add the body for each step to the page body
        var body = $('.body-wrapper');
        var before;

        updates.forEach(function (update) {
          var existing = $('[data-step-name="' + update.name + '"]');
          if (update.action === 'removed') {
            existing.remove();
            return;
          }

          var stepDom = exports.prepareStepBody(update.step);
          if (selectedStep && update.name === selectedStep.name) {
            setSelected(stepDom);
          }

          if (update.action === 'updated') {
            existing.replaceWith(stepDom);
            return;
          }

          if (update.action === 'modified') {
            stepDom = body.find('[data-step-name="' + update.name + '"]');
            stepDom.find('.cd-step-title').html(update.title || update.name);
            stepDom.detach();
          }

          // Modified or added steps get inserted into the dom
          if (update.after) {
            before = body.find('[data-step-name="' + update.after + '"]');
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
      });
  }
  exports.processStepUpdates = processStepUpdates;

}());
