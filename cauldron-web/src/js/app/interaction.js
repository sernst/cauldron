import $ from 'jquery';

/**
 * Scrolls the display to the location specified by the step name
 *
 * @param stepName
 *  The name of the step to scroll the display to
 * @param location
 *  The named location where the scroll should be located. Accepted values
 *  include:
 *   * 'end' to scroll to show the bottom of the step
 *   * 'error' to scroll to show the error in the step (if any)
 *   * null to scroll to show the top of the step (default)
 * @param animationSpeed
 *  The enumerated animation speed, 'fast' or 'slow'. The default is slow.
 */
function scrollToAnchor(stepName, location, animationSpeed) {
  const windowHeight = $(window).height();
  const stepDom = $('.body-wrapper')
    .find(`.cd-project-step[data-step-name='${stepName}']`);

  // Don't use locations if the step dom height is short
  const isShortDom = stepDom.height() < (windowHeight - 100);
  const anchorName = (location && !isShortDom)
    ? `${stepName}--${location}`
    : stepName;

  function getOffset() {
    if (isShortDom) {
      return 0;
    }

    if (location === 'end') {
      return windowHeight - 100;
    }

    return 0;
  }

  const body = $('body');
  const aTag = stepDom.find(`a[name='${anchorName}']`);
  const scrollTop = (aTag.offset().top - getOffset()); // + body.scrollTop();

  // console.log('SCROLLING:', {
  //   location,
  //   animationSpeed,
  //   scrollTop,
  //   windowHeight,
  //   isShortDom,
  //   anchorName,
  //   bodyScrollTop: body.scrollTop(),
  //   aTagOffset: aTag.offset().top,
  //   stepHeight: stepDom.height()
  // });

  body
    .stop(true)
    .animate({ scrollTop }, animationSpeed || 'slow');
}


/**
 *
 * @param selector
 */
function toggleVisible(selector) {
  $(selector).toggle();
}


/**
 *
 * @param buttonId
 */
function collapse(buttonId) {
  const btn = $(`#${buttonId}`);
  const open = btn.hasClass('closed');
  const items = btn.attr(`data-${open ? 'opens' : 'closes'}`);
  const marksList = btn.attr(`data-marks-${open ? 'opened' : 'closed'}`) || '';
  const marks = marksList.split('|').map((selector) => $(selector));

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

  setTimeout(
    () => $(window).resize(),
    100
  );
}

/**
 *
 * @param target
 * @param direction
 */
function changeFontSize(target, direction) {
  const codeBox = $(target);

  function getSize() {
    if (!direction) {
      return parseFloat(codeBox.attr('data-font-size-default'));
    }

    const current = parseFloat(codeBox.attr('data-font-size'));
    return Math.max(0.1, current + (direction * 0.1));
  }

  const size = getSize();
  codeBox
    .attr('data-font-size', size)
    .css('font-size', `${size}em`);
}

export default {
  scrollToAnchor,
  changeFontSize,
  collapse,
  toggleVisible
};
