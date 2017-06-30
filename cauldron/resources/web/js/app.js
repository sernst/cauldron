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

"use strict";function scrollToAnchor(e,o,t){var s=$(window).height(),a=$(".body-wrapper").find(".cd-project-step[data-step-name='"+e+"']"),n=a.height()<s-100,r=o&&!n?e+"--"+o:e,i=$("body"),l=a.find("a[name='"+r+"']").offset().top-function(){if(n)return 0;switch(o){case"end":return s-100;default:return 0}}();i.stop(!0).animate({scrollTop:l},t||"slow")}function toggleVisible(e){$(e).toggle()}function collapse(e){var o=$("#"+e),t=o.hasClass("closed"),s=o.attr("data-"+(t?"opens":"closes")),a=(o.attr("data-marks-"+(t?"opened":"closed"))||"").split("|").map(function(e){return $(e)});a.push(o),a.forEach(function(e){t?e.removeClass("closed").addClass("opened"):e.removeClass("opened").addClass("closed")}),s?(s.split("|").forEach(function(e){var s=$(e);t?(s.show(),o.removeClass("closed")):(s.hide(),s.addClass("closed"))}),setTimeout(function(){return $(window).resize()},100)):$(window).resize()}function changeFontSize(e,o){var t=$(e),s=function(){if(!o)return parseFloat(t.attr("data-font-size-default"));var e=parseFloat(t.attr("data-font-size"));return Math.max(.1,e+.1*o)}();t.attr("data-font-size",s).css("font-size",s+"em")}var _exports=window.CAULDRON||{};window.CAULDRON=_exports,_exports.scrollToAnchor=scrollToAnchor,_exports.toggleVisible=toggleVisible,_exports.collapse=collapse,_exports.changeFontSize=changeFontSize;
}());

;(function() {
"use strict";

"use strict";function loadSourceFile(e){function r(e,r){setTimeout(function(){return e(r)},250)}var o=void 0,n="?nocache="+_exports.getNoCacheString();return o=e.src.startsWith(":")?e.src.slice(1):_exports.DATA_DIRECTORY+e.src,window.document.getElementById(e.name)?Promise.resolve():/.*\.css$/.test(o)?new Promise(function(t){var i=document.createElement("link");i.rel="stylesheet",i.onload=r.bind(null,t,i),i.href=o+n,i.id=e.name,document.head.appendChild(i)}):/.*\.js$/.test(o)?new Promise(function(t){var i=document.createElement("script");i.onload=r.bind(null,t,i),i.src=o+n,i.id=e.name,document.head.appendChild(i)}):Promise.reject()}function loadSourceFiles(e){if(!e)return Promise.resolve([]);var r=e.map(function(e){return _exports.loadSourceFile(e)});return Promise.all(r)}function loadStepIncludes(e){if(!e)return Promise.resolve([]);var r=e.filter(function(e){return e}).map(function(e){return _exports.loadSourceFiles(e.includes)});return Promise.all(r)}var _exports=window.CAULDRON||{};window.CAULDRON=_exports,_exports.loadSourceFile=loadSourceFile,_exports.loadSourceFiles=loadSourceFiles,_exports.loadStepIncludes=loadStepIncludes;
}());

;(function() {
"use strict";

"use strict";function onWindowResize(){if(_exports.RUNNING&&!resizePaused){var e=$(window).width();Math.abs(e-previousWidth)<10||(previousWidth=e,_exports.resizeCallbacks.forEach(function(e){return e()}),_exports.resizePlotly())}}function resizePlotlyBox(e){var i=$(e),s=i.parent();i.parents(".cd-project-step-body").hasClass("closed")||resizePaused||window.Plotly.relayout(i[0],{width:s.width(),height:s.height()})}function resizePlotly(){window.Plotly&&$(".cd-plotly-box").each(function(e,i){var s=$(i).find(".plotly-graph-div");_exports.resizePlotlyBox(s)})}function pauseResizing(){resizePaused=!0}function resumeResizing(){resizePaused=!1,setTimeout(onWindowResize,100)}var _exports=window.CAULDRON||{};window.CAULDRON=_exports;var previousWidth=-100,resizePaused=!1;window.onresize=onWindowResize,_exports.resizePlotlyBox=resizePlotlyBox,_exports.resizePlotly=resizePlotly,_exports.pauseResizing=pauseResizing,_exports.resumeResizing=resumeResizing;
}());

;(function() {
"use strict";

"use strict";function isNumeric(r){return!(!r||/[^0-9.-]+/.test(r))&&(!((r.match(/\.+/g)||[]).length>1)&&-1===r.slice(1).indexOf("-"))}function parseUrlValue(r){return isNumeric(r)?-1===r.indexOf(".")?parseInt(r,10):parseFloat(r):"true"===r.toLowerCase()||"false"!==r.toLowerCase()&&decodeURIComponent(r)}function parseUrlParameters(){return document.location.search.replace(/(^\?)/,"").split("&").map(function(r){return r.split("=")}).filter(function(r){return 2===r.length}).reduce(function(r,e){var t=_slicedToArray(e,2),n=t[0],a=t[1],o=r;return o[n]=parseUrlValue(a),o},{})}var _slicedToArray=function(){function r(r,e){var t=[],n=!0,a=!1,o=void 0;try{for(var i,u=r[Symbol.iterator]();!(n=(i=u.next()).done)&&(t.push(i.value),!e||t.length!==e);n=!0);}catch(r){a=!0,o=r}finally{try{!n&&u.return&&u.return()}finally{if(a)throw o}}return t}return function(e,t){if(Array.isArray(e))return e;if(Symbol.iterator in Object(e))return r(e,t);throw new TypeError("Invalid attempt to destructure non-iterable instance")}}(),_exports=window.CAULDRON||{};window.CAULDRON=_exports,_exports.parseUrlParameters=parseUrlParameters;
}());

;(function() {
"use strict";

"use strict";function addRenameAttribute(e,t,r){var n=t[r],a=e.find('[data-step-name="'+r+'"]');a.attr("data-step-rename",n.name),a.find(".cd-step-title").html(n.title||n.name)}function renameStep(e){var t=$(e),r=t.attr("data-step-rename");t.attr("data-step-rename",null).attr("data-step-name",r).find(".step-anchor").each(function(e,t){var n=$(t);n.attr("name",""+r+n.attr("data-type"))})}function onProcessingReady(e){var t=$(".body-wrapper");return Object.keys(e).forEach(function(r){return addRenameAttribute(t,e,r)}),t.find("[data-step-rename]").each(function(e,t){return renameStep(t)}),Promise.resolve(e)}function processStepRenames(e){return e?(processingPromise||(processingPromise=window.CD.on.ready),processingPromise=processingPromise.then(function(){return onProcessingReady(e)})):Promise.resolve(e)}var _exports=window.CAULDRON||{};window.CAULDRON=_exports;var processingPromise=void 0;_exports.processStepRenames=processStepRenames;
}());

;(function() {
"use strict";

"use strict";function setSelected(e){if(e&&!e.hasClass("cd-project-step--selected")){e.addClass("cd-project-step--selected");var t=e.find(".cd-project-step__header");t.addClass("cd-project-step__header--selected").removeClass(t.attr("data-default-modifier"))}}function removeSelected(e){e.removeClass("cd-project-step--selected");var t=e.find(".cd-project-step__header");t.removeClass("cd-project-step__header--selected").addClass(t.attr("data-default-modifier"))}function doSelectionUpdate(){var e=selectedStep;selectionTimeout=null,e&&$(".body-wrapper").find(".cd-project-step").each(function(t,r){var o=$(r);o.attr("data-step-name")===e.name?setSelected(o):removeSelected(o)})}function updateSelectedStep(e){return e&&(selectedStep=e),selectionTimeout?Promise.resolve(selectedStep):new Promise(function(e){selectionTimeout=setTimeout(function(){doSelectionUpdate(),e(selectedStep)},10)})}function prepareStepBody(e){function t(e){var t=e.attr("data-src");return t&&t.startsWith("/")?t.slice(1):t}if(!e||!e.body)return null;var r=$(e.body);return r.find("[data-src]").each(function(e,r){var o=$(r),s=t(o);o.attr("src",_exports.DATA_DIRECTORY+"/"+s+"?nocache="+_exports.getNoCacheString()),o.attr("data-src",null)}),r}function onReadyToProcess(e){var t=$(".body-wrapper"),r=void 0;e.forEach(function(e){var o=$('[data-step-name="'+e.name+'"]');if("removed"!==e.action){var s=_exports.prepareStepBody(e.step);selectedStep&&e.name===selectedStep.name&&setSelected(s),"updated"!==e.action?("modified"===e.action&&((s=t.find('[data-step-name="'+e.name+'"]')).find(".cd-step-title").html(e.title||e.name),s.detach()),(r=e.after?t.find('[data-step-name="'+e.after+'"]'):t.find(".cd-body-header").after(s))&&r.length>0?r.after(s):e.after?t.append(s):t.prepend(s)):o.replaceWith(s)}else o.remove()}),$(window).trigger("resize"),_exports.updateSelectedStep()}function processStepUpdates(e,t){if(!e)return Promise.resolve();processingPromise||(processingPromise=window.CD.on.ready),t&&(selectedStep=t);var r=e.map(function(e){return e.step});return processingPromise=processingPromise.then(function(){return _exports.loadStepIncludes(r)}).then(function(){return onReadyToProcess(e)})}var _exports=window.CAULDRON||{};window.CAULDRON=_exports;var selectedStep=void 0,selectionTimeout=void 0,processingPromise=void 0;_exports.updateSelectedStep=updateSelectedStep,_exports.prepareStepBody=prepareStepBody,_exports.processStepUpdates=processStepUpdates;
}());

;(function() {
"use strict";

"use strict";function populateDom(){_exports.addSnapshotBar(),$("title").text(_exports.TITLE),_exports.SETTINGS.headerless||(_exports.createHeader(),$(".cd-body-header").find(".project-title").text(_exports.TITLE))}function start(){_exports.RUNNING=!0,_exports.__on__.ready(),$(window).resize()}var _exports=window.CAULDRON||{};window.CAULDRON=_exports,_exports.RUNNING=!1,$(function(){_exports.PARAMS=_exports.parseUrlParameters(),_exports.initialize().then(populateDom).then(start)});
}());
