/* global $ */

const exports = window.CAULDRON || {};
window.CAULDRON = exports;


/**
 *
 * @param name
 * @param location
 * @param animationSpeed
 */
function scrollToAnchor(name, location, animationSpeed) {
  const stepDom = $('.body-wrapper')
    .find(`.cd-project-step[data-step-name='${name}']`);

  // Don't use locations if the step dom height is short
  const isShortDom = stepDom.height() < ($(window).height() - 100);
  const anchorName = (isShortDom || !location) ? name : `${name}--${location}`;

  function getOffset() {
    switch (location) {
      case 'end':
        return $(window).height() - 100;
      default:
        return 0;
    }
  }

  const body = $('body');
  const aTag = $(`a[name='${anchorName}']`);
  const scrollTop = (aTag.offset().top - getOffset()) + body.scrollTop();

  body
    .stop(true)
    .animate({ scrollTop }, animationSpeed || 'slow');
}
exports.scrollToAnchor = scrollToAnchor;


/**
 *
 * @param selector
 */
function toggleVisible(selector) {
  $(selector).toggle();
}
exports.toggleVisible = toggleVisible;


/**
 *
 * @param buttonId
 */
function collapse(buttonId) {
  const btn = $(`#${buttonId}`);
  const open = btn.hasClass('closed');
  const items = btn.attr(`data-${open ? 'opens' : 'closes'}`);
  const marksList = btn.attr(`data-marks-${open ? 'opened' : 'closed'}`) || '';
  const marks = marksList.split('|').map(selector => $(selector));

  marks.push(btn);
  marks.forEach((target) => {
    if (open) {
      target.removeClass('closed').addClass('opened');
    } else {
      target.removeClass('opened').addClass('closed');
    }
  });

  if (!items) {
    $(window).resize();
    return;
  }

  items.split('|').forEach((target) => {
    const t = $(target);
    if (open) {
      t.show();
      btn.removeClass('closed');
    } else {
      t.hide();
      t.addClass('closed');
    }
  });

  $(window).resize();
}
exports.collapse = collapse;


/**
 *
 * @param target
 * @param direction
 */
function changeFontSize(target, direction) {
  function getSize() {
    if (!direction) {
      return parseFloat(target.attr('data-font-size-default'));
    }

    const current = parseFloat(target.attr('data-font-size'));
    return Math.max(0.1, current + (direction * 0.1));
  }

  const size = getSize();
  $(target)
    .attr('data-font-size', size)
    .css('font-size', `${size}em`);
}
exports.changeFontSize = changeFontSize;
