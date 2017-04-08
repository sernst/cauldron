;(function() {
"use strict";

"use strict";function getNoCacheString(){var t=new Date;return[t.getUTCMilliseconds(),t.getUTCSeconds(),t.getUTCMinutes(),t.getUTCHours(),t.getUTCDay(),t.getUTCMonth(),t.getUTCFullYear()].join("-")}function capitalize(t){return t.replace(/(?:^|\s)\S/g,function(t){return t.toUpperCase()})}function toDisplayNumber(t,e){function r(t){return(.01*Math.round(100*t)).toFixed(2)}return r(t)+" &#177; "+r(e)}var _exports=window.CAULDRON||{};window.CAULDRON=_exports,_exports.getNoCacheString=getNoCacheString,_exports.capitalize=capitalize,_exports.toDisplayNumber=toDisplayNumber;
}());

;(function() {
"use strict";

"use strict";function fakeRequire(t,o){var r=[];t.forEach(function(t){"plotly"===t&&r.push(window.Plotly)}),o.apply(this,r)}function getDataDirectory(){if(window.PROJECT_DIRECTORY)return window.PROJECT_DIRECTORY;if(_exports.PARAMS.data_root)return _exports.PARAMS.data_root;var t=_exports.PARAMS.id||window.PROJECT_ID,o=_exports.PARAMS.sid;return["reports",t||"",o?"snapshots":"latest",o||""].filter(function(t){return t.length>0}).join("/")}function addSnapshotBar(){var t=_exports.PARAMS.sid,o=$("body");return!!t&&($("<div></div>").addClass("snapshot-bar").text("Snapshot: "+t).prependTo(o),$("<div></div>").addClass("snapshot-bar").addClass("snapshot-bar-overlay").text("Snapshot: "+_exports.PARAMS.sid).prependTo(o),_exports.TITLE="{"+t+"} "+_exports.TITLE,!0)}function loadProjectData(){return window.RESULTS?Promise.resolve():window.RESULTS_FILENAME?_exports.loadSourceFile({name:"cauldron-project",src:":"+window.RESULTS_FILENAME}):_exports.loadSourceFile({name:"cauldron-project",src:"/results.js"})}function initialize(){return _exports.DATA_DIRECTORY=getDataDirectory(),loadProjectData().then(function(){return window.CAULDRON_VERSION=window.RESULTS.cauldron_version,_exports.RESULTS=window.RESULTS,_exports.DATA=window.RESULTS.data,_exports.SETTINGS=window.RESULTS.settings,_exports.TITLE=_exports.SETTINGS.title||_exports.SETTINGS.id||id,_exports.loadSourceFiles(window.RESULTS.includes)}).then(function(){return _exports.loadStepIncludes(_exports.RESULTS.steps)}).then(function(){var t=$(".body-wrapper");return window.RESULTS.steps.forEach(function(o){var r=_exports.prepareStepBody(o);r&&t.append(r)}),$(window).trigger("resize"),_exports.DATA})}var _exports=window.CAULDRON||{};window.CAULDRON=_exports,_exports.resizeCallbacks=[],window.require=fakeRequire,_exports.addSnapshotBar=addSnapshotBar,_exports.initialize=initialize;
}());

;(function() {
"use strict";

"use strict";function createHeader(){var e=$(headerDom.join("")).prependTo($(".body-wrapper"));_exports.RESULTS.has_error&&e.addClass("project-error")}var _exports=window.CAULDRON||{};window.CAULDRON=_exports;var headerDom=['<div class="cd-body-header">','<div class="menu-icon"></div>','<div class="project-title"></div>','<div class="spacer"></div>','<div class="buttons"></div>',"</div>"];_exports.createHeader=createHeader;
}());

;(function() {
"use strict";

"use strict";function scrollToAnchor(e,o,t){var s=$(window).height(),a=$(".body-wrapper").find(".cd-project-step[data-step-name='"+e+"']"),r=a.height()<s-100,n=o&&!r?e+"--"+o:e,l=$("body"),i=$("a[name='"+n+"']"),c=i.offset().top-function(){if(r)return 0;switch(o){case"end":return s-100;default:return 0}}()+l.scrollTop();l.stop(!0).animate({scrollTop:c},t||"slow")}function toggleVisible(e){$(e).toggle()}function collapse(e){var o=$("#"+e),t=o.hasClass("closed"),s=o.attr("data-"+(t?"opens":"closes")),a=o.attr("data-marks-"+(t?"opened":"closed"))||"",r=a.split("|").map(function(e){return $(e)});if(r.push(o),r.forEach(function(e){t?e.removeClass("closed").addClass("opened"):e.removeClass("opened").addClass("closed")}),!s)return void $(window).resize();s.split("|").forEach(function(e){var s=$(e);t?(s.show(),o.removeClass("closed")):(s.hide(),s.addClass("closed"))}),$(window).resize()}function changeFontSize(e,o){var t=$(e),s=function(){if(!o)return parseFloat(t.attr("data-font-size-default"));var e=parseFloat(t.attr("data-font-size"));return Math.max(.1,e+.1*o)}();t.attr("data-font-size",s).css("font-size",s+"em")}var _exports=window.CAULDRON||{};window.CAULDRON=_exports,_exports.scrollToAnchor=scrollToAnchor,_exports.toggleVisible=toggleVisible,_exports.collapse=collapse,_exports.changeFontSize=changeFontSize;
}());

;(function() {
"use strict";

"use strict";function loadSourceFile(e){function r(e,r){setTimeout(function(){return e(r)},250)}var o=void 0,n="?nocache="+_exports.getNoCacheString();return o=e.src.startsWith(":")?e.src.slice(1):_exports.DATA_DIRECTORY+e.src,window.document.getElementById(e.name)?Promise.resolve():/.*\.css$/.test(o)?new Promise(function(t){var i=document.createElement("link");i.rel="stylesheet",i.onload=r.bind(null,t,i),i.href=o+n,i.id=e.name,document.head.appendChild(i)}):/.*\.js$/.test(o)?new Promise(function(t){var i=document.createElement("script");i.onload=r.bind(null,t,i),i.src=o+n,i.id=e.name,document.head.appendChild(i)}):Promise.reject()}function loadSourceFiles(e){if(!e)return Promise.resolve([]);var r=e.map(function(e){return _exports.loadSourceFile(e)});return Promise.all(r)}function loadStepIncludes(e){if(!e)return Promise.resolve([]);var r=e.filter(function(e){return e}).map(function(e){return _exports.loadSourceFiles(e.includes)});return Promise.all(r)}var _exports=window.CAULDRON||{};window.CAULDRON=_exports,_exports.loadSourceFile=loadSourceFile,_exports.loadSourceFiles=loadSourceFiles,_exports.loadStepIncludes=loadStepIncludes;
}());

;(function() {
"use strict";

"use strict";function onWindowResize(){if(_exports.RUNNING){var o=$(window).width();Math.abs(o-previousWidth)<10||(previousWidth=o,_exports.resizeCallbacks.forEach(function(o){return o()}),_exports.resizePlotly())}}function resizePlotly(){window.Plotly&&$(".cd-plotly-box").each(function(o,e){var i=$(e);i.parents(".cd-project-step-body").hasClass("closed")||window.Plotly.relayout(i.find(".plotly-graph-div")[0],{width:i.width(),height:i.height()})})}var _exports=window.CAULDRON||{};window.CAULDRON=_exports;var previousWidth=-100;window.onresize=onWindowResize,_exports.resizePlotly=resizePlotly;
}());

;(function() {
"use strict";

"use strict";function isNumeric(r){return!(!r||/[^0-9.-]+/.test(r))&&(!((r.match(/\.+/g)||[]).length>1)&&-1===r.slice(1).indexOf("-"))}function parseUrlValue(r){return isNumeric(r)?-1===r.indexOf(".")?parseInt(r,10):parseFloat(r):"true"===r.toLowerCase()||"false"!==r.toLowerCase()&&decodeURIComponent(r)}function parseUrlParameters(){return document.location.search.replace(/(^\?)/,"").split("&").map(function(r){return r.split("=")}).filter(function(r){return 2===r.length}).reduce(function(r,e){var t=_slicedToArray(e,2),n=t[0],a=t[1],o=r;return o[n]=parseUrlValue(a),o},{})}var _slicedToArray=function(){function r(r,e){var t=[],n=!0,a=!1,o=void 0;try{for(var i,u=r[Symbol.iterator]();!(n=(i=u.next()).done)&&(t.push(i.value),!e||t.length!==e);n=!0);}catch(r){a=!0,o=r}finally{try{!n&&u.return&&u.return()}finally{if(a)throw o}}return t}return function(e,t){if(Array.isArray(e))return e;if(Symbol.iterator in Object(e))return r(e,t);throw new TypeError("Invalid attempt to destructure non-iterable instance")}}(),_exports=window.CAULDRON||{};window.CAULDRON=_exports,_exports.parseUrlParameters=parseUrlParameters;
}());

;(function() {
"use strict";

"use strict";function addRenameAttribute(e,t,a){var r=t[a],n=e.find('[data-step-name="'+a+'"]');n.attr("data-step-rename",r.name),n.find(".cd-step-title").html(r.title||r.name)}function renameStep(e){var t=$(e),a=t.attr("data-step-rename");t.attr("data-step-rename",null).attr("data-step-name",a).find(".step-anchor").each(function(e,t){var r=$(t);r.attr("name",""+a+r.attr("data-type"))})}function processStepRenames(e){if(!e)return Promise.resolve(e);var t=$(".body-wrapper");return Object.keys(e).forEach(function(a){return addRenameAttribute(t,e,a)}),t.find("[data-step-rename]").each(function(e,t){return renameStep(t)}),Promise.resolve(e)}var _exports=window.CAULDRON||{};window.CAULDRON=_exports,_exports.processStepRenames=processStepRenames;
}());

;(function() {
"use strict";

"use strict";function setSelected(e){if(e&&!e.hasClass("cd-project-step--selected")){e.addClass("cd-project-step--selected");var t=e.find(".cd-project-step__header");t.addClass("cd-project-step__header--selected").removeClass(t.attr("data-default-modifier"))}}function removeSelected(e){e.removeClass("cd-project-step--selected");var t=e.find(".cd-project-step__header");t.removeClass("cd-project-step__header--selected").addClass(t.attr("data-default-modifier"))}function doSelectionUpdate(){var e=selectedStep;selectionTimeout=null,e&&$(".body-wrapper").find(".cd-project-step").each(function(t,r){var d=$(r);d.attr("data-step-name")===e.name?setSelected(d):removeSelected(d)})}function updateSelectedStep(e){return e&&(selectedStep=e),selectionTimeout?Promise.resolve(selectedStep):new Promise(function(e){function t(){doSelectionUpdate(),e(selectedStep)}selectionTimeout=setTimeout(t,10)})}function prepareStepBody(e){function t(e){var t=e.attr("data-src");return t&&t.startsWith("/")?t.slice(1):t}if(!e||!e.body)return null;var r=$(e.body);return r.find("[data-src]").each(function(e,r){var d=$(r),a=t(d);d.attr("src",_exports.DATA_DIRECTORY+"/"+a+"?nocache="+_exports.getNoCacheString()),d.attr("data-src",null)}),r}function processStepUpdates(e,t){if(!e)return null;t&&(selectedStep=t);var r=e.map(function(e){return e.step});return _exports.loadStepIncludes(r).then(function(){var t=$(".body-wrapper"),r=void 0;e.forEach(function(e){var d=$('[data-step-name="'+e.name+'"]');if("removed"===e.action)return void d.remove();var a=_exports.prepareStepBody(e.step);if(selectedStep&&e.name===selectedStep.name&&setSelected(a),"updated"===e.action)return void d.replaceWith(a);"modified"===e.action&&(a=t.find('[data-step-name="'+e.name+'"]'),a.find(".cd-step-title").html(e.title||e.name),a.detach()),r=e.after?t.find('[data-step-name="'+e.after+'"]'):t.find(".cd-body-header").after(a),r&&r.length>0?r.after(a):e.after?t.append(a):t.prepend(a)}),$(window).trigger("resize"),_exports.updateSelectedStep()})}var _exports=window.CAULDRON||{};window.CAULDRON=_exports;var selectedStep=void 0,selectionTimeout=void 0;_exports.updateSelectedStep=updateSelectedStep,_exports.prepareStepBody=prepareStepBody,_exports.processStepUpdates=processStepUpdates;
}());

;(function() {
"use strict";

"use strict";function populateDom(){_exports.addSnapshotBar(),$("title").text(_exports.TITLE),_exports.SETTINGS.headerless||(_exports.createHeader(),$(".cd-body-header").find(".project-title").text(_exports.TITLE))}function start(){_exports.RUNNING=!0,_exports.__on__.ready(),$(window).resize()}var _exports=window.CAULDRON||{};window.CAULDRON=_exports,_exports.RUNNING=!1,$(function(){_exports.PARAMS=_exports.parseUrlParameters(),_exports.initialize().then(populateDom).then(start)});
}());
