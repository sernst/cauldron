;(function() {
"use strict";

"use strict";!function(){function n(n,o){var i=[];n.forEach(function(n){"plotly"===n&&i.push(window.Plotly)}),o.apply(this,i)}function o(){var n=window.PROJECT_DIRECTORY,o=e.PARAMS.id||window.PROJECT_ID,i=e.PARAMS.sid;return n||(n=["reports"],o&&n.push(o),i?(n.push("snapshots"),n.push(i)):n.push("latest"),n=n.join("/")),e.DATA_DIRECTORY=n,n}function i(){var n=e.PARAMS.sid,o=$("body");return!!n&&($("<div></div>").addClass("snapshot-bar").text("Snapshot: "+e.PARAMS.sid).prependTo(o),$("<div></div>").addClass("snapshot-bar").addClass("snapshot-bar-overlay").text("Snapshot: "+e.PARAMS.sid).prependTo(o),void(e.TITLE="{"+n+"} "+e.TITLE))}function r(){var n;return o(),n=window.RESULTS?Promise.resolve():window.RESULTS_FILENAME?e.loadSourceFile({name:"cauldron-project",src:":"+window.RESULTS_FILENAME}):e.loadSourceFile({name:"cauldron-project",src:"/results.js"}),n.then(function(){return window.CAULDRON_VERSION=window.RESULTS.cauldron_version,e.RESULTS=window.RESULTS,e.DATA=window.RESULTS.data,e.SETTINGS=window.RESULTS.settings,e.TITLE=e.SETTINGS.title||e.SETTINGS.id||id,e.loadSourceFiles(window.RESULTS.includes)}).then(function(){return e.loadStepIncludes(e.RESULTS.steps)}).then(function(){var n=$(".body-wrapper");return window.RESULTS.steps.forEach(function(o){var i=e.prepareStepBody(o);i&&n.append(i)}),$(window).trigger("resize"),e.DATA})}var e=window.CAULDRON||{};window.CAULDRON=e,e.resizeCallbacks=[],window.require=n,e.addSnapshotBar=i,e.initialize=r}();
}());

;(function() {
"use strict";

"use strict";!function(){function d(){var d=$(r.join("")).prependTo($(".body-wrapper"));i.RESULTS.has_error&&d.addClass("project-error");d.find(".buttons")}var i=window.CAULDRON||{};window.CAULDRON=i;var r=['<div class="cd-body-header">','<div class="menu-icon"></div>','<div class="project-title"></div>','<div class="spacer"></div>','<div class="buttons"></div>',"</div>"];i.createHeader=d}();
}());

;(function() {
"use strict";

"use strict";!function(){function e(e,t,a){function o(){switch(t){case"end":return $(window).height()-100;default:return 0}}var s=$(".body-wrapper").find('.cd-project-step[data-step-name="'+e+'"]');s.height()<$(window).height()-100&&(t=null);var n=e;t&&t.length>0&&(n+="--"+t);var d=$("a[name='"+n+"']");$("html,body").animate({scrollTop:d.offset().top-o()},a||"slow")}function t(e){$(e).toggle()}function a(e){var t=$("#"+e),a=t.hasClass("closed"),o=t.attr("data-"+(a?"opens":"closes")),s=t.attr("data-marks-"+(a?"opened":"closed"))||"";return s=s.split("|").map(function(e){return $(e)}),s.push(t),s.forEach(function(e){a?e.removeClass("closed").addClass("opened"):e.removeClass("opened").addClass("closed")}),o?(o.split("|").forEach(function(e){e=$(e),a?(e.show(),t.removeClass("closed")):(e.hide(),e.addClass("closed"))}),void $(window).resize()):void $(window).resize()}function o(e,t){e=$(e);var a=parseFloat(e.attr("data-font-size"));a=t?Math.max(.1,a+.1*t):parseFloat(e.attr("data-font-size-default")),e.attr("data-font-size",a),e.css("font-size",a+"em")}var s=window.CAULDRON||{};window.CAULDRON=s,s.scrollToAnchor=e,s.toggleVisible=t,s.collapse=a,s.changeFontSize=o}();
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

"use strict";!function(){function e(e){if(e&&!e.hasClass("cd-project-step--selected")){e.addClass("cd-project-step--selected");var t=e.find(".cd-project-step__header");t.addClass("cd-project-step__header--selected").removeClass(t.attr("data-default-modifier"))}}function t(e){e.removeClass("cd-project-step--selected");var t=e.find(".cd-project-step__header");t.removeClass("cd-project-step__header--selected").addClass(t.attr("data-default-modifier"))}function a(){var a=c;return i=null,a?(console.log("SELECTED:",a),void $(".body-wrapper").find(".cd-project-step").each(function(r,n){var d=$(n),o=d.attr("data-step-name");o===a.name?e(d):t(d)})):null}function r(e){return e&&(c=e),console.log("UPDATING SELECTED:",c),i?Promise.resolve(c):new Promise(function(e){function t(){a(),e(c)}i=setTimeout(t,10)})}function n(e){if(!e||!e.body)return null;var t=$(e.body);return t.find("[data-src]").each(function(e,t){var a=$(t),r=a.attr("data-src");r.startsWith("/")&&(r=r.slice(1)),a.attr("src",s.DATA_DIRECTORY+"/"+r+"?nocache="+s.getNoCacheString()),a.attr("data-src",null)}),t}function d(e){if(!e)return Promise.resolve(e);var t=$(".body-wrapper");return Object.keys(e).forEach(function(a){var r=e[a],n=t.find('[data-step-name="'+a+'"]');n.attr("data-step-rename",r.name),n.find(".cd-step-title").html(r.title||r.name)}),t.find("[data-step-rename]").each(function(e,t){var a=$(t),r=a.attr("data-step-rename");a.attr("data-step-rename",null),a.attr("data-step-name",r),a.find(".step-anchor").attr("name",r)}),Promise.resolve(e)}function o(t,a){if(t){a&&(c=a);var r=t.map(function(e){return e.step});return s.loadStepIncludes(r).then(function(){var a,r=$(".body-wrapper");t.forEach(function(t){var n=$('[data-step-name="'+t.name+'"]');if("removed"===t.action)return void n.remove();var d=s.prepareStepBody(t.step);return c&&t.name===c.name&&e(d),"updated"===t.action?void n.replaceWith(d):("modified"===t.action&&(d=r.find('[data-step-name="'+t.name+'"]'),d.find(".cd-step-title").html(t.title||t.name),d.detach()),a=t.after?r.find('[data-step-name="'+t.after+'"]'):r.find(".cd-body-header").after(d),void(a&&a.length>0?a.after(d):t.after?r.append(d):r.prepend(d)))}),$(window).trigger("resize"),s.updateSelectedStep()})}}var s=window.CAULDRON||{};window.CAULDRON=s;var c,i;s.updateSelectedStep=r,s.prepareStepBody=n,s.processStepRenames=d,s.processStepUpdates=o}();
}());

;(function() {
"use strict";

"use strict";!function(){function t(){var t=new Date;return t.getUTCMilliseconds()+"-"+t.getUTCSeconds()+"-"+t.getUTCMinutes()+"-"+t.getUTCHours()+"-"+t.getUTCDay()+"-"+t.getUTCMonth()+"-"+t.getUTCFullYear()}function e(t){return(t?this.toLowerCase():this).replace(/(?:^|\s)\S/g,function(t){return t.toUpperCase()})}function n(t,e){return(.01*Math.round(100*t)).toFixed(2)+" &#177; "+(.01*Math.round(100*e)).toFixed(2)}var o=window.CAULDRON||{};window.CAULDRON=o,o.getNoCacheString=t,o.capitalize=e,o.toDisplayNumber=n}();
}());

;(function() {
"use strict";

"use strict";!function(){function e(){var e={};return document.location.search.replace(/(^\?)/,"").split("&").forEach(function(t){if(t=t.split("="),!(t.length<2)){var n=t[1];n=/[^0-9\.]+/.test(n)?"true"===n.toLowerCase()||"false"!==n.toLowerCase()&&decodeURIComponent(n):n.indexOf(".")===-1?parseInt(n,10):parseFloat(n),e[t[0]]=n}}),e}function t(){return n.initialize().then(function(){$("body");n.addSnapshotBar(),$("title").text(n.TITLE),n.SETTINGS.headerless||(n.createHeader(),$(".cd-body-header").find(".project-title").text(n.TITLE))})}var n=window.CAULDRON||{};window.CAULDRON=n,n.RUNNING=!1,n.parseUrlParameters=e,n.run=t,$(function(){n.PARAMS=n.parseUrlParameters(),n.run().then(function(){n.RUNNING=!0,n.__on__.ready(),$(window).resize()})})}();
}());
