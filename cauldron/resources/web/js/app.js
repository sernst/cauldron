;(function() {
"use strict";

"use strict";!function(){function t(){var t=new Date;return t.getUTCMilliseconds()+"-"+t.getUTCSeconds()+"-"+t.getUTCMinutes()+"-"+t.getUTCHours()+"-"+t.getUTCDay()+"-"+t.getUTCMonth()+"-"+t.getUTCFullYear()}function e(t){return(t?this.toLowerCase():this).replace(/(?:^|\s)\S/g,function(t){return t.toUpperCase()})}function n(t,e){return(.01*Math.round(100*t)).toFixed(2)+" &#177; "+(.01*Math.round(100*e)).toFixed(2)}var o=window.CAULDRON||{};window.CAULDRON=o,o.getNoCacheString=t,o.capitalize=e,o.toDisplayNumber=n}();
}());

;(function() {
"use strict";

"use strict";function fakeRequire(e,o){var r=[];e.forEach(function(e){"plotly"===e&&r.push(window.Plotly)}),o.apply(this,r)}function getDataDirectory(){if(window.PROJECT_DIRECTORY)return window.PROJECT_DIRECTORY;var e=_exports.PARAMS.id||window.PROJECT_ID,o=_exports.PARAMS.sid,r=["reports"];return e&&r.push(e),o?(r.push("snapshots"),r.push(o)):r.push("latest"),r.join("/")}function addSnapshotBar(){var e=_exports.PARAMS.sid,o=$("body");return!!e&&($("<div></div>").addClass("snapshot-bar").text("Snapshot: "+e).prependTo(o),$("<div></div>").addClass("snapshot-bar").addClass("snapshot-bar-overlay").text("Snapshot: "+_exports.PARAMS.sid).prependTo(o),_exports.TITLE="{"+e+"} "+_exports.TITLE,!0)}function loadProjectData(){return window.RESULTS?Promise.resolve():window.RESULTS_FILENAME?_exports.loadSourceFile({name:"cauldron-project",src:":"+window.RESULTS_FILENAME}):_exports.loadSourceFile({name:"cauldron-project",src:"/results.js"})}function initialize(){return _exports.DATA_DIRECTORY=getDataDirectory(),loadProjectData().then(function(){return window.CAULDRON_VERSION=window.RESULTS.cauldron_version,_exports.RESULTS=window.RESULTS,_exports.DATA=window.RESULTS.data,_exports.SETTINGS=window.RESULTS.settings,_exports.TITLE=_exports.SETTINGS.title||_exports.SETTINGS.id||id,_exports.loadSourceFiles(window.RESULTS.includes)}).then(function(){return _exports.loadStepIncludes(_exports.RESULTS.steps)}).then(function(){var e=$(".body-wrapper");return window.RESULTS.steps.forEach(function(o){var r=_exports.prepareStepBody(o);r&&e.append(r)}),$(window).trigger("resize"),_exports.DATA})}var _exports=window.CAULDRON||{};window.CAULDRON=_exports,_exports.resizeCallbacks=[],window.require=fakeRequire,_exports.addSnapshotBar=addSnapshotBar,_exports.initialize=initialize;
}());

;(function() {
"use strict";

"use strict";function createHeader(){var e=$(headerDom.join("")).prependTo($(".body-wrapper"));_exports.RESULTS.has_error&&e.addClass("project-error")}var _exports=window.CAULDRON||{};window.CAULDRON=_exports;var headerDom=['<div class="cd-body-header">','<div class="menu-icon"></div>','<div class="project-title"></div>','<div class="spacer"></div>','<div class="buttons"></div>',"</div>"];_exports.createHeader=createHeader;
}());

;(function() {
"use strict";

"use strict";function scrollToAnchor(e,o,t){function s(){switch(o){case"end":return $(window).height()-100;default:return 0}}var a=$(".body-wrapper").find('.cd-project-step[data-step-name="'+e+'"]'),n=a.height()<$(window).height()-100,r=n||!o?e:e+"--"+o,l=$("body"),i=$("a[name='"+r+"']"),c=i.offset().top-s()+l.scrollTop();l.stop(!0).animate({scrollTop:c},t||"slow")}function toggleVisible(e){$(e).toggle()}function collapse(e){var o=$("#"+e),t=o.hasClass("closed"),s=o.attr("data-"+(t?"opens":"closes")),a=o.attr("data-marks-"+(t?"opened":"closed"))||"",n=a.split("|").map(function(e){return $(e)});return n.push(o),n.forEach(function(e){t?e.removeClass("closed").addClass("opened"):e.removeClass("opened").addClass("closed")}),s?(s.split("|").forEach(function(e){var s=$(e);t?(s.show(),o.removeClass("closed")):(s.hide(),s.addClass("closed"))}),void $(window).resize()):void $(window).resize()}function changeFontSize(e,o){function t(){if(!o)return parseFloat(e.attr("data-font-size-default"));var t=parseFloat(e.attr("data-font-size"));return Math.max(.1,t+.1*o)}var s=t();$(e).attr("data-font-size",s).css("font-size",s+"em")}var _exports=window.CAULDRON||{};window.CAULDRON=_exports,_exports.scrollToAnchor=scrollToAnchor,_exports.toggleVisible=toggleVisible,_exports.collapse=collapse,_exports.changeFontSize=changeFontSize;
}());

;(function() {
"use strict";

"use strict";!function(){function e(e){var r,n="?nocache="+o.getNoCacheString();r=e.src.startsWith(":")?e.src.slice(1):o.DATA_DIRECTORY+e.src;var t=window.document.getElementById(e.name);return t?Promise.resolve():/.*\.css$/.test(r)?new Promise(function(o){var t=document.createElement("link");t.rel="stylesheet",t.onload=o,t.href=r+n,t.id=e.name,document.head.appendChild(t)}):/.*\.js$/.test(r)?new Promise(function(o){var t=document.createElement("script");t.onload=o,t.src=r+n,t.id=e.name,document.head.appendChild(t)}):Promise.reject()}function r(e){if(!e)return Promise.resolve([]);var r=[];return e.forEach(function(e){r.push(o.loadSourceFile(e))}),Promise.all(r)}function n(e){if(!e)return Promise.resolve([]);var r=[];return e.forEach(function(e){e&&r.push(o.loadSourceFiles(e.includes))}),Promise.all(r)}var o=window.CAULDRON||{};window.CAULDRON=o,o.loadSourceFile=e,o.loadSourceFiles=r,o.loadStepIncludes=n}();
}());

;(function() {
"use strict";

"use strict";!function(){function i(){if(o.RUNNING){var i=$(window).width();Math.abs(i-e)<10||(e=i,o.resizeCallbacks.forEach(function(i){i()}),o.resizePlotly())}}function t(){$(".cd-plotly-box").each(function(i,t){var o=$(t),e=o.parents(".cd-project-step-body").hasClass("closed");e||Plotly.relayout(o.find(".plotly-graph-div")[0],{width:o.width(),height:o.height()})})}var o=window.CAULDRON||{};window.CAULDRON=o;var e=-100;window.onresize=i,o.resizePlotly=t}();
}());

;(function() {
"use strict";

"use strict";function setSelected(e){if(e&&!e.hasClass("cd-project-step--selected")){e.addClass("cd-project-step--selected");var t=e.find(".cd-project-step__header");t.addClass("cd-project-step__header--selected").removeClass(t.attr("data-default-modifier"))}}function removeSelected(e){e.removeClass("cd-project-step--selected");var t=e.find(".cd-project-step__header");t.removeClass("cd-project-step__header--selected").addClass(t.attr("data-default-modifier"))}function doSelectionUpdate(){var e=selectedStep;selectionTimeout=null,e&&(console.log("SELECTED:",e),$(".body-wrapper").find(".cd-project-step").each(function(t,a){var r=$(a),d=r.attr("data-step-name");d===e.name?setSelected(r):removeSelected(r)}))}function updateSelectedStep(e){return e&&(selectedStep=e),console.log("UPDATING SELECTED:",selectedStep),selectionTimeout?Promise.resolve(selectedStep):new Promise(function(e){function t(){doSelectionUpdate(),e(selectedStep)}selectionTimeout=setTimeout(t,10)})}function prepareStepBody(e){function t(e){var t=e.attr("data-src");return t.startsWith("/")?t.slice(1):t}if(!e||!e.body)return null;var a=$(e.body);return a.find("[data-src]").each(function(e,a){var r=$(a),d=t(r);r.attr("src",_exports.DATA_DIRECTORY+"/"+d+"?nocache="+_exports.getNoCacheString()),r.attr("data-src",null)}),a}function processStepRenames(e){if(!e)return Promise.resolve(e);var t=$(".body-wrapper");return Object.keys(e).forEach(function(a){var r=e[a],d=t.find('[data-step-name="'+a+"\"]'");d.attr("data-step-rename",r.name),d.find(".cd-step-title").html(r.title||r.name)}),t.find("[data-step-rename]").each(function(e,t){var a=$(t),r=a.attr("data-step-rename");a.attr("data-step-rename",null).attr("data-step-name",r).find(".step-anchor").attr("name",r)}),Promise.resolve(e)}function processStepUpdates(e,t){if(!e)return null;t&&(selectedStep=t);var a=e.map(function(e){return e.step});return _exports.loadStepIncludes(a).then(function(){var t=$(".body-wrapper"),a=void 0;e.forEach(function(e){var r=$('[data-step-name="'+e.name+'"]');if("removed"===e.action)return void r.remove();var d=_exports.prepareStepBody(e.step);return selectedStep&&e.name===selectedStep.name&&setSelected(d),"updated"===e.action?void r.replaceWith(d):("modified"===e.action&&(d=t.find('[data-step-name="'+e.name+'"]'),d.find(".cd-step-title").html(e.title||e.name),d.detach()),a=e.after?t.find('[data-step-name="'+e.after+'"]'):t.find(".cd-body-header").after(d),void(a&&a.length>0?a.after(d):e.after?t.append(d):t.prepend(d)))}),$(window).trigger("resize"),_exports.updateSelectedStep()})}var _exports=window.CAULDRON||{};window.CAULDRON=_exports;var selectedStep=void 0,selectionTimeout=void 0;_exports.updateSelectedStep=updateSelectedStep,_exports.prepareStepBody=prepareStepBody,_exports.processStepRenames=processStepRenames,_exports.processStepUpdates=processStepUpdates;
}());

;(function() {
"use strict";

"use strict";function isNumeric(r){if(!r||/[^0-9.-]+/.test(r))return!1;var e=(r.match(/\.+/g)||[]).length;return!(e>1)&&r.slice(1).indexOf("-")===-1}function parseUrlValue(r){return isNumeric(r)?r.indexOf(".")===-1?parseInt(r,10):parseFloat(r):"true"===r.toLowerCase()||"false"!==r.toLowerCase()&&decodeURIComponent(r)}function parseUrlParameters(){return document.location.search.replace(/(^\?)/,"").split("&").forEach(function(r){return r.split("=")}).filter(function(r){return 2===r.length}).reduce(function(r,e){var t=_slicedToArray(e,2),n=t[0],a=t[1],o=r;return o[n]=parseUrlValue(a),o},{})}var _slicedToArray=function(){function r(r,e){var t=[],n=!0,a=!1,o=void 0;try{for(var i,u=r[Symbol.iterator]();!(n=(i=u.next()).done)&&(t.push(i.value),!e||t.length!==e);n=!0);}catch(r){a=!0,o=r}finally{try{!n&&u.return&&u.return()}finally{if(a)throw o}}return t}return function(e,t){if(Array.isArray(e))return e;if(Symbol.iterator in Object(e))return r(e,t);throw new TypeError("Invalid attempt to destructure non-iterable instance")}}(),_exports=window.CAULDRON||{};window.CAULDRON=_exports,_exports.parseUrlParameters=parseUrlParameters;
}());

;(function() {
"use strict";

"use strict";function populateDom(){_exports.addSnapshotBar(),$("title").text(_exports.TITLE),_exports.SETTINGS.headerless||(_exports.createHeader(),$(".cd-body-header").find(".project-title").text(_exports.TITLE))}function start(){_exports.RUNNING=!0,_exports.__on__.ready(),$(window).resize()}var _exports=window.CAULDRON||{};window.CAULDRON=_exports,_exports.RUNNING=!1,$(function(){_exports.PARAMS=_exports.parseUrlParameters(),_exports.initialize().then(populateDom).then(start)});
}());
