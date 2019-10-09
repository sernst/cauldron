import $ from 'jquery';

import utils from './utils';

const headerDom = [
  '<div class="cd-body-header">',
  '<div class="menu-icon"></div>',
  '<div class="project-title"></div>',
  '<div class="spacer"></div>',
  '<div class="buttons"></div>',
  '</div>'
];

/**
 *
 */
function createHeader() {
  const cauldron = utils.getRoot();
  const header = $(headerDom.join(''))
    .prependTo($('.body-wrapper'));

  if (cauldron.RESULTS.has_error) {
    header.addClass('project-error');
  }
}

export default { createHeader };
