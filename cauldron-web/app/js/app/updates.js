(function () {
  'use strict';

  var exports = window.CAULDRON || {};
  window.CAULDRON = exports;


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
   *
   * @param renames
   */
  function processStepRenames(renames) {
    console.log('RENAMES:', renames);
    if (!renames) {
      return Promise.resolve(renames);
    }

    var body = $('.body-wrapper');

    Object.keys(renames).forEach(function (oldName) {
      var data = renames[oldName];
      var stepBody = body.find('[data-step-name="' + oldName + '"]');
      stepBody.attr('data-step-name', data.name);
      stepBody.find('.step-anchor').attr('name', data.name);
      stepBody.find('.cd-step-title').html(data.title || data.name);
    });

    return Promise.resolve(renames);
  }
  exports.processStepRenames = processStepRenames;


  /**
   *
   */
  function processStepUpdates(updates) {
    console.log('UPDATES:', updates);
    if (!updates) {
      return;
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

            var stepBody = exports.prepareStepBody(update.step);

            if (update.action === 'updated') {
              existing.replaceWith(stepBody);
              return;
            }

            if (update.action === 'modified') {
              stepBody = body.find('[data-step-name="' + update.name + '"]');
              stepBody.find('.cd-step-title').html(update.title || update.name);
              stepBody.detach();
            }

            // Modified or added steps get inserted into the dom
            if (update.after) {
              before = body.find('[data-step-name="' + update.after + '"]');
            } else {
              before = body.find('.cd-body-header').after(stepBody);
            }

            if (before && before.length > 0) {
              before.after(stepBody);
            } else if (update.after) {
              body.append(stepBody);
            } else {
              body.prepend(stepBody);
            }

          });

          $(window).trigger('resize');
        });
  }
  exports.processStepUpdates = processStepUpdates;

}());
