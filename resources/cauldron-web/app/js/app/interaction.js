(function () {
  'use strict';

  var exports = window.CAULDRON || {};
  window.CAULDRON = exports;

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
   * @param id
   * @param open
   */
  function collapse(id, open) {
    var e = $('#' + id);
    var body = e.children('.body');
    var code = e.children('.code');
    var opener = e.children('.header').find('.collapse-open');
    var closer = e.children('.header').find('.collapse-close');

    if (open) {
      e.removeClass('collapsed');
      body.show();
      opener.hide();
      closer.show();
      $(window).resize();
    } else {
      e.addClass('collapsed');
      body.hide();
      code.hide();
      closer.hide();
      opener.show();
    }
  }
  exports.collapse = collapse;


}());
