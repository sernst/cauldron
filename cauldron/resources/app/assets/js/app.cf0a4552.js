(function(e){function t(t){for(var r,o,i=t[0],c=t[1],u=t[2],l=0,d=[];l<i.length;l++)o=i[l],Object.prototype.hasOwnProperty.call(a,o)&&a[o]&&d.push(a[o][0]),a[o]=0;for(r in c)Object.prototype.hasOwnProperty.call(c,r)&&(e[r]=c[r]);p&&p(t);while(d.length)d.shift()();return s.push.apply(s,u||[]),n()}function n(){for(var e,t=0;t<s.length;t++){for(var n=s[t],r=!0,o=1;o<n.length;o++){var i=n[o];0!==a[i]&&(r=!1)}r&&(s.splice(t--,1),e=c(c.s=n[0]))}return e}var r={},o={app:0},a={app:0},s=[];function i(e){return c.p+"assets/js/"+({"create~project":"create~project",create:"create",project:"project"}[e]||e)+"."+{"create~project":"48b68943",create:"5f3503e1",project:"9b6477fc"}[e]+".js"}function c(t){if(r[t])return r[t].exports;var n=r[t]={i:t,l:!1,exports:{}};return e[t].call(n.exports,n,n.exports,c),n.l=!0,n.exports}c.e=function(e){var t=[],n={"create~project":1,create:1,project:1};o[e]?t.push(o[e]):0!==o[e]&&n[e]&&t.push(o[e]=new Promise((function(t,n){for(var r="assets/css/"+({"create~project":"create~project",create:"create",project:"project"}[e]||e)+"."+{"create~project":"588b048f",create:"019b4dfd",project:"0beac151"}[e]+".css",a=c.p+r,s=document.getElementsByTagName("link"),i=0;i<s.length;i++){var u=s[i],l=u.getAttribute("data-href")||u.getAttribute("href");if("stylesheet"===u.rel&&(l===r||l===a))return t()}var d=document.getElementsByTagName("style");for(i=0;i<d.length;i++){u=d[i],l=u.getAttribute("data-href");if(l===r||l===a)return t()}var p=document.createElement("link");p.rel="stylesheet",p.type="text/css",p.onload=t,p.onerror=function(t){var r=t&&t.target&&t.target.src||a,s=new Error("Loading CSS chunk "+e+" failed.\n("+r+")");s.code="CSS_CHUNK_LOAD_FAILED",s.request=r,delete o[e],p.parentNode.removeChild(p),n(s)},p.href=a;var f=document.getElementsByTagName("head")[0];f.appendChild(p)})).then((function(){o[e]=0})));var r=a[e];if(0!==r)if(r)t.push(r[2]);else{var s=new Promise((function(t,n){r=a[e]=[t,n]}));t.push(r[2]=s);var u,l=document.createElement("script");l.charset="utf-8",l.timeout=120,c.nc&&l.setAttribute("nonce",c.nc),l.src=i(e);var d=new Error;u=function(t){l.onerror=l.onload=null,clearTimeout(p);var n=a[e];if(0!==n){if(n){var r=t&&("load"===t.type?"missing":t.type),o=t&&t.target&&t.target.src;d.message="Loading chunk "+e+" failed.\n("+r+": "+o+")",d.name="ChunkLoadError",d.type=r,d.request=o,n[1](d)}a[e]=void 0}};var p=setTimeout((function(){u({type:"timeout",target:l})}),12e4);l.onerror=l.onload=u,document.head.appendChild(l)}return Promise.all(t)},c.m=e,c.c=r,c.d=function(e,t,n){c.o(e,t)||Object.defineProperty(e,t,{enumerable:!0,get:n})},c.r=function(e){"undefined"!==typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},c.t=function(e,t){if(1&t&&(e=c(e)),8&t)return e;if(4&t&&"object"===typeof e&&e&&e.__esModule)return e;var n=Object.create(null);if(c.r(n),Object.defineProperty(n,"default",{enumerable:!0,value:e}),2&t&&"string"!=typeof e)for(var r in e)c.d(n,r,function(t){return e[t]}.bind(null,r));return n},c.n=function(e){var t=e&&e.__esModule?function(){return e["default"]}:function(){return e};return c.d(t,"a",t),t},c.o=function(e,t){return Object.prototype.hasOwnProperty.call(e,t)},c.p="/v1/app/",c.oe=function(e){throw console.error(e),e};var u=window["webpackJsonp"]=window["webpackJsonp"]||[],l=u.push.bind(u);u.push=t,u=u.slice();for(var d=0;d<u.length;d++)t(u[d]);var p=l;s.push([0,"chunk-vendors"]),n()})({0:function(e,t,n){e.exports=n("56d7")},"025e":function(e,t,n){"use strict";n("d3b7");function r(e){return Object({NODE_ENV:"production",BASE_URL:"/v1/app/",BUILD_MODE:"prod",UI_VERSION:"0.2.0"})[e]}function o(e,t){return new Promise((function(n){setTimeout((function(){n(t)}),e)}))}t["a"]={thenWait:o,getBuildVar:r}},"04e4":function(e,t,n){},"14ab":function(e,t,n){},"1aaf":function(e,t,n){"use strict";var r=n("7e5d"),o=n.n(r);o.a},"1f1d":function(e,t,n){"use strict";var r=n("14ab"),o=n.n(r);o.a},2423:function(e,t,n){e.exports=n.p+"assets/img/logo-128.a32de47b.png"},"3fa3":function(e,t,n){"use strict";n("99af"),n("4de4"),n("13d5"),n("b0c0"),n("b64b"),n("d3b7"),n("ac1f"),n("5319");var r=n("5530"),o=n("ade3"),a=n("025e"),s=n("c0d6"),i=Math.round((new Date).getTime()/1e3);function c(){var e=window.location.origin,t=window.location.pathname.replace("app/project","notebook");return"".concat(e).concat(t,"/display.html?no-cache=").concat(i)}function u(){var e=s["a"].getters.view;if(!e)return"";var t=window.location.origin,n=window.location.pathname.replace("/app",""),r=encodeURIComponent("".concat(n,"/cache/").concat(e.id));return"".concat(t).concat(n,"/notebook/project.html?no-cache=").concat(i,"&data_root=").concat(r)}function l(){return document.querySelector(".Notebook__frame")}function d(){i=Math.round((new Date).getTime()/1e3);var e=l();e&&e.contentWindow.location.reload()}function p(){try{var e=l();return((e||{}).contentWindow||{}).CAULDRON}catch(t){return null}}function f(e,t){var n=p();if(n)if(e)n.scrollToAnchor(e,t);else{var r=(s["a"].getters.project||{}).steps||[],o=r.filter((function(e){var t=e.status.running||e.name===s["a"].getters.runningStepName;return t&&(e.status.selected||s["a"].getters.followSteps)}));if(0!==o.length){var a=o[0].status.error?"error":"end";n.scrollToAnchor(o[0].name,t||a)}}}function v(e){var t=s["a"].getters.previousStepChanges;return e.filter((function(e){var n=t[e.name]||{},r=(e.step||{}).body||"",o=(n.step||{}).body||"",a=e.timestamp||1,s=n.timestamp||0;return"added"===e.action||"removed"===e.action||r!==o&&a>s}))}function m(e,t,n){var i=v(t||[]),c=0===Object.keys(e||{}).length&&0===(i||[]).length;if(c)return Promise.resolve();var u=p();return u?u.processStepRenames(e||{}).then((function(){u.processStepUpdates(i);var e=s["a"].getters.previousStepChanges,t=i.reduce((function(e,t){return Object.assign(e,Object(o["a"])({},t.name,t))}),{}),n=Object(r["a"])(Object(r["a"])({},e),t);return s["a"].commit("previousStepChanges",n),a["a"].thenWait(300)})).then((function(){if(n||s["a"].getters.followSteps){var e=(s["a"].getters.project||{}).steps||[],r=e.filter((function(e){return e.name===n})).concat(t.filter((function(e){return e.step})).reverse());if(0!==r.length){var o=r[0],a=(o.status||{}).error;f(o.name,a?"error":"end")}}})):Promise.resolve()}function h(){return new Promise((function(e,t){var n=0,r=0,o=setInterval((function(){var a=p(),i=s["a"].getters,c=i.project,u=i.view;return c||u?a&&a.on&&a.on.ready?a.RUNNING?(clearInterval(o),void a.on.ready.then((function(){return e(a)}))):(r+=1,void(r>10&&(r=0,console.warn("Notebook load running timeout reached. Refreshing..."),d()))):(n+=1,void(n>10&&(n=0,console.warn("Notebook load wait timeout reached. Refreshing..."),d()))):(clearInterval(o),void t())}),200)}))}t["a"]={applyStepModifications:m,getUrl:c,getViewUrl:u,getCauldronObject:p,getIframe:l,refresh:d,onLoaded:h,scrollToStep:f}},"46aa":function(e,t,n){"use strict";var r=n("7d32"),o=n.n(r);o.a},"56d7":function(e,t,n){"use strict";n.r(t);n("e260"),n("e6cf"),n("cca6"),n("a79d");var r=n("a026"),o=n("6018"),a=function(){var e=this,t=e.$createElement,n=e._self._c||t;return n("div",{staticClass:"App",attrs:{id:"app"}},[n("router-view",{staticClass:"App__routerView"}),e.warning?n("warning-overlay",{attrs:{warning:e.warning},on:{close:e.onDismissWarning}}):e._e(),e.error?n("error-overlay",{attrs:{error:e.error},on:{close:e.onDismissError}}):e._e(),e.showLostConnection?n("lost-connection-overlay"):e._e(),e.loadingMessage.id?n("loader",{attrs:{message:e.loadingMessage.message}}):e._e()],1)},s=[],i=(n("99af"),n("c975"),n("d81d"),n("fb6a"),n("a434"),n("d3b7"),n("2ca0"),n("ba6a")),c=function(){var e=this,t=e.$createElement,n=e._self._c||t;return n("div",{staticClass:"WarningOverlay"},[n("div",{staticClass:"WarningOverlay__focus"},[n("div",{staticClass:"WarningOverlay__headerBox"},[n("i",{staticClass:"WarningOverlay__icon material-icons md-36"},[e._v("warning")]),n("div",{staticClass:"WarningOverlay__titleBox"},[n("div",{staticClass:"WarningOverlay__titleHeader"},[e._v("Warning")]),n("div",{staticClass:"WarningOverlay__title"},[e._v(e._s(e.warning.code))])])]),n("div",{staticClass:"WarningOverlay__infoBox"},[n("div",{staticClass:"WarningOverlay__message"},[e._v(e._s(e.warning.message))])]),n("div",{staticClass:"WarningOverlay__buttonBox"},[n("div",{staticClass:"WarningOverlay__spacer"}),n("button",{staticClass:"WarningOverlay__button button is-small is-dark",on:{click:e.onDismiss}},[e._v("OK")])])])])},u=[];function l(){return{}}function d(){this.$emit("close")}var p={name:"WarningOverlay",props:{warning:{type:Object,default:function(){}}},data:l,methods:{onDismiss:d}},f=p,v=(n("1f1d"),n("2877")),m=Object(v["a"])(f,c,u,!1,null,"15015cde",null),h=m.exports,g=function(){var e=this,t=e.$createElement,n=e._self._c||t;return n("div",{staticClass:"ErrorOverlay"},[n("div",{staticClass:"ErrorOverlay__focus"},[n("div",{staticClass:"ErrorOverlay__headerBox"},[n("i",{staticClass:"ErrorOverlay__icon material-icons md-36"},[e._v("error_outline")]),n("div",{staticClass:"ErrorOverlay__titleBox"},[n("div",{staticClass:"ErrorOverlay__titleHeader"},[e._v("Error")]),n("div",{staticClass:"ErrorOverlay__title"},[e._v(e._s(e.error.code))])])]),n("div",{staticClass:"ErrorOverlay__infoBox"},[n("div",{staticClass:"ErrorOverlay__message"},[e._v(e._s(e.error.message))])]),n("div",{staticClass:"ErrorOverlay__buttonBox"},[n("div",{staticClass:"ErrorOverlay__spacer"}),n("button",{staticClass:"ErrorOverlay__button button is-small",on:{click:e.onDismiss}},[e._v("OK")])])])])},_=[];function y(){return{}}function C(){this.$emit("close")}var b={name:"ErrorOverlay",props:{error:{type:Object,default:function(){}}},data:y,methods:{onDismiss:C}},w=b,S=(n("ff27"),Object(v["a"])(w,g,_,!1,null,"1dde40ec",null)),O=S.exports,j=n("726c"),R=function(){var e=this,t=e.$createElement;e._self._c;return e._m(0)},x=[function(){var e=this,t=e.$createElement,n=e._self._c||t;return n("div",{staticClass:"LostConnectionOverlay"},[n("div",{staticClass:"LostConnectionOverlay__focus"},[n("div",{staticClass:"LostConnectionOverlay__headerBox"},[n("i",{staticClass:"LostConnectionOverlay__icon material-icons md-36"},[e._v("signal_wifi_off")]),n("div",{staticClass:"LostConnectionOverlay__titleBox"},[n("div",{staticClass:"LostConnectionOverlay__titleHeader"},[e._v("No Response")]),n("div",{staticClass:"LostConnectionOverlay__title"},[e._v("Lost Kernel Connection")])])]),n("div",{staticClass:"LostConnectionOverlay__infoBox"},[n("div",{staticClass:"LostConnectionOverlay__message"},[e._v("Trying to re-establish communication with the Cauldron kernel...")])])])])}],E={name:"LostConnectionOverlay"},k=E,T=(n("771f"),Object(v["a"])(k,R,x,!1,null,"73a56477",null)),P=T.exports,L=n("025e"),N=n("ea2f"),H="success",W="failure",I="lost";function M(){var e=this.$store.getters.loadingMessages||[];return e.length>0?e.splice(-1)[0]:{}}function $(){var e=this.$store.getters.warnings;return e.length<1?null:e[0]}function D(){var e=this.$store.getters.warnings.concat();e.length<1||(e.shift(),this.$store.commit("warnings",e))}function q(){var e=this.$store.getters.errors;return e.length<1?null:e[0]}function B(){var e=this.$store.getters.errors.concat();e.length<1||(e.shift(),this.$store.commit("errors",e))}function V(e,t){return this.recentResponses.push({kind:e,responseOrError:t,success:e===H}),this.recentResponses.length>50&&this.recentResponses.shift(),t}function A(){var e=this,t=this.$store.getters,n=t.isStatusDirty,r=t.isNotebookLoading,o=t.errors,a=t.warnings;if(o.length>0||a.length>0)return n||this.$store.commit("isStatusDirty",!0),clearTimeout(this.timeoutHandle),this.timeoutHandle=setTimeout(this.updateStatusLoop,100),Promise.resolve();if(r)return clearTimeout(this.timeoutHandle),this.timeoutHandle=setTimeout(this.updateStatusLoop,200),Promise.resolve();n&&this.$store.commit("isStatusDirty",!1);var s=this.$store.getters.running?500:1e3;return i["a"].updateStatus(n?0:s).then((function(t){if(t.data.success)return e.recordResponse(H,t),t;var n=t.data.errors.map((function(e){return e.code}));return-1!==n.indexOf("LOST_REMOTE_CONNECTION")?e.recordResponse(I,t):(e.recordResponse(W,t),console.error("Failed update response",t.data),t)})).catch((function(t){return t.request?"ECONNABORTED"===t.code||408===(t.response||{}).status?(e.recordResponse(I,t),L["a"].thenWait(200)):t.response?(e.recordResponse(W,t),L["a"].thenWait(200)):(e.recordResponse(I,t),L["a"].thenWait(500)):(e.recordResponse(W,t),j["a"].addError({code:"UNKNOWN_ERROR",message:"Malformed request attempt has halted communication with the kernel."}),console.warn(t),Promise.resolve())})).finally((function(){var t=e.$router.currentRoute.path,n=e.$store.getters,r=n.project,o=n.view;o&&!t.startsWith("/view")?e.$router.push("/view"):o||!r||t.startsWith("/project")?(null===r&&t.startsWith("/project")||null===o&&t.startsWith("/view"))&&e.$router.push("/"):e.$router.push("/project"),clearTimeout(e.timeoutHandle),e.timeoutHandle=setTimeout(e.updateStatusLoop,100)}))}function U(){if(0===this.recentResponses.length)return!1;var e=this.recentResponses.slice(-1)[0].kind;return e===I}function F(){return{timeoutHandle:null,recentResponses:[]}}function z(){return this.updateStatusLoop()}function K(){clearInterval(this.timeoutHandle)}var Q={name:"App",components:{Loader:N["a"],LostConnectionOverlay:P,ErrorOverlay:O,WarningOverlay:h},data:F,computed:{warning:$,error:q,showLostConnection:U,loadingMessage:M},mounted:z,beforeDestroy:K,methods:{recordResponse:V,updateStatusLoop:A,onDismissWarning:D,onDismissError:B}},G=Q,J=(n("5c0b"),Object(v["a"])(G,a,s,!1,null,null,null)),X=J.exports,Y=n("8c4f"),Z=function(){var e=this,t=e.$createElement,n=e._self._c||t;return n("div",{staticClass:"Home"},[n("div",{staticClass:"Home__splash"},[n("div",{staticClass:"Home__focus"},[n("img",{staticClass:"Home__logo",attrs:{src:e.logo}}),n("div",{staticClass:"Home__title"},[e._v("Cauldron")]),n("div",{staticClass:"Home__tagline"},[n("div",[e._v("Interactive Computing Environment")]),n("div",{staticClass:"Home__version"},[n("div",{staticClass:"Home__versionPrefix"},[e._v("Kernel:")]),n("div",{staticClass:"Home__versionValue",class:e.versionClasses},[e._v("v"+e._s(e.info.version))]),n("div",{staticClass:"Home__versionPrefix"},[e._v("Python:")]),n("div",{staticClass:"Home__versionValue",class:e.pythonVersionClasses},[e._v("v"+e._s(e.info.python_version))])]),n("div",{staticClass:"Home__version"},[n("div",{staticClass:"Home__versionPrefix"},[e._v("Server:")]),n("div",{staticClass:"Home__versionValue",class:e.versionClasses},[e._v("v"+e._s(e.info.ui_server_version))]),n("div",{staticClass:"Home__versionPrefix"},[e._v("Python:")]),n("div",{staticClass:"Home__versionValue",class:e.pythonVersionClasses},[e._v("v"+e._s(e.info.ui_python_version))])]),n("div",{staticClass:"Home__version"},[n("div",{staticClass:"Home__versionPrefix"},[e._v("Web:")]),n("div",{staticClass:"Home__versionValue"},[e._v("v"+e._s(e.uiVersion))]),n("div",{staticClass:"Home__versionPrefix"},[e._v("Notebook:")]),n("div",{staticClass:"Home__versionValue"},[e._v(e._s(e.info.notebook_version))])])]),n("div",{staticClass:"Home__buttonBox"},[n("div",{staticClass:"button Home__button tooltip",attrs:{"data-tooltip":"A new notebook project"},on:{click:e.createProject}},[e._v("Create")]),n("div",{staticClass:"button Home__button tooltip",attrs:{"data-tooltip":"An existing notebook project from a local directory"},on:{click:e.openProjectBrowser}},[e._v("Open")])])]),n("remote-connect",{staticClass:"Home__remoteConnect",attrs:{status:e.info}})],1),e.recentProjects.length>0?n("div",{staticClass:"Home__recent"},e._l(e.recentProjects,(function(t){return n("recent-item",{attrs:{item:t},on:{click:e.onProjectClick}})})),1):e._e(),e.loadingMessage?n("loader",{attrs:{message:e.loadingMessage}}):e._e()],1)},ee=[],te=(n("b0c0"),n("ac1f"),n("1276"),n("96cf"),n("1da1")),ne=n("2423"),re=n.n(ne),oe=function(){var e=this,t=e.$createElement,n=e._self._c||t;return n("div",{staticClass:"RecentItem",on:{click:e.openProject}},[e._m(0),n("div",{staticClass:"RecentItem__box"},[n("div",{staticClass:"RecentItem__title"},[e._v(e._s(e.item.name))]),n("div",{staticClass:"RecentItem__path"},[e._v(e._s(e.item.directory.short))]),n("div",{directives:[{name:"tippy",rawName:"v-tippy",value:{placement:"top"},expression:"{ placement: 'top' }"}],staticClass:"RecentItem__date",attrs:{content:e.item.modified.display}},[e._v(e._s(e.item.modified.elapsed))])]),n("div",{staticClass:"RecentItem__rightBox"},[n("div",{staticClass:"RecentItem__remove tooltip is-tooltip-left is-tooltip-danger",attrs:{"data-tooltip":"Remove from recent list"},on:{click:function(t){return t.stopPropagation(),e.removeFromRecent(t)}}},[n("i",{staticClass:"material-icons md-18"},[e._v("close")])])])])},ae=[function(){var e=this,t=e.$createElement,n=e._self._c||t;return n("div",{staticClass:"RecentItem__leftBox"},[n("div",{staticClass:"material-icons RecentItem__icon"},[e._v("folder_open")])])}];function se(e){return this.$emit("click",{action:"remove",event:e,item:this.item})}function ie(e){return this.$emit("click",{action:"open",event:e,item:this.item})}var ce={name:"RecentItem",props:{item:{type:Object,default:function(){}}},methods:{openProject:ie,removeFromRecent:se}},ue=ce,le=(n("46aa"),Object(v["a"])(ue,oe,ae,!1,null,"48a6cff4",null)),de=le.exports,pe=function(){var e=this,t=e.$createElement,n=e._self._c||t;return n("div",{staticClass:"RemoteConnect tooltip is-tooltip-right",class:{"RemoteConnect--connected":e.connected,"RemoteConnect--disconnected":!e.connected},attrs:{"data-tooltip":e.tooltip}},[n("div",{staticClass:"material-icons"},[e._v(e._s(e.icon))])])},fe=[];function ve(){var e,t,n=this.connected?"remote":"local",r=(null===(e=this.status)||void 0===e||null===(t=e.remote)||void 0===t?void 0:t.url)||null,o=this.connected?"at ".concat(r):"alongside the UI.";return"Running a ".concat(n," kernel connection ").concat(o)}function me(){return this.connected?"link":"link_off"}function he(){var e,t;return(null===(e=this.status)||void 0===e||null===(t=e.remote)||void 0===t?void 0:t.active)||!1}var ge={name:"RemoteConnect",props:{status:{type:Object,default:function(){}}},computed:{connected:he,icon:me,tooltip:ve}},_e=ge,ye=(n("82dc"),Object(v["a"])(_e,pe,fe,!1,null,"8b90a7e4",null)),Ce=ye.exports;function be(){return L["a"].getBuildVar("UI_VERSION")||"???"}function we(){try{var e=this.info.version.split("."),t=this.info.ui_server_version.split(".");return e[0]!==t[0]||e[1]!==t[1]?["Home__versionValue--danger"]:e[2]!==t[2]?["Home__versionValue--warning"]:[]}catch(n){return[]}}function Se(){try{var e=this.info.python_version.split("."),t=this.info.ui_python_version.split(".");return e[0]!==t[0]||e[1]!==t[1]?["Home__versionValue--danger"]:e[2]!==t[2]?["Home__versionValue--warning"]:[]}catch(n){return[]}}function Oe(){return this.$router.push("/create")}function je(){return this.$router.push("/open")}function Re(e){return xe.apply(this,arguments)}function xe(){return xe=Object(te["a"])(regeneratorRuntime.mark((function e(t){var n,r,o,a,s;return regeneratorRuntime.wrap((function(e){while(1)switch(e.prev=e.next){case 0:if(n=t.item.uid,"remove"!==t.action){e.next=9;break}return this.loadingMessage="Removing Recent Project Entry",e.next=5,i["a"].execute("list erase ".concat(n," --yes"));case 5:return r=e.sent,this.recentProjects=r.data.data.projects,this.loadingMessage=null,e.abrupt("return");case 9:return o=t.item.name,a=t.item.directory.absolute,this.loadingMessage='Loading "'.concat(o,'" Project'),e.next=14,i["a"].execute('open "'.concat(a,'"'));case 14:s=e.sent,i["a"].markStatusDirty(),s.data.success||(this.loadingMessage=null);case 17:case"end":return e.stop()}}),e,this)}))),xe.apply(this,arguments)}function Ee(){return{logo:re.a,loadingMessage:"Synchronizing with Cauldron Kernel",info:{notebook_version:"v0",version:"0.0.0",ui_server_version:"0.0.0",python_version:"0.0.0",ui_python_version:"0.0.0"},recentProjects:[]}}function ke(){return Te.apply(this,arguments)}function Te(){return Te=Object(te["a"])(regeneratorRuntime.mark((function e(){var t,n;return regeneratorRuntime.wrap((function(e){while(1)switch(e.prev=e.next){case 0:return e.next=2,i["a"].updateStatus(500);case 2:return t=e.sent,this.info=t.data.data,e.next=6,i["a"].execute("list recent");case 6:n=e.sent,this.recentProjects=n.data.data.projects,this.loadingMessage=null;case 9:case"end":return e.stop()}}),e,this)}))),Te.apply(this,arguments)}var Pe={name:"Home",components:{Loader:N["a"],RecentItem:de,RemoteConnect:Ce},data:Ee,computed:{uiVersion:be,versionClasses:we,pythonVersionClasses:Se},mounted:ke,methods:{createProject:Oe,onProjectClick:Re,openProjectBrowser:je}},Le=Pe,Ne=(n("c3b6"),Object(v["a"])(Le,Z,ee,!1,null,"08461924",null)),He=Ne.exports;r["a"].use(Y["a"]);var We=new Y["a"]({mode:"history",base:"/v1/app/",routes:[{path:"/",name:"home",component:He},{path:"/project",name:"project",component:function(){return Promise.all([n.e("create~project"),n.e("project")]).then(n.bind(null,"b7bc"))}},{path:"/create",name:"create",component:function(){return Promise.all([n.e("create~project"),n.e("create")]).then(n.bind(null,"f28d"))}},{path:"/open",name:"open",component:function(){return Promise.all([n.e("create~project"),n.e("create")]).then(n.bind(null,"8d29"))}},{path:"/view",name:"viewer",component:function(){return Promise.all([n.e("create~project"),n.e("create")]).then(n.bind(null,"03e7"))}}]}),Ie=n("c0d6");r["a"].use(o["b"]),r["a"].component("tippy",o["a"]),r["a"].config.productionTip=!1,new r["a"]({router:We,store:Ie["a"],render:function(e){return e(X)}}).$mount("#app")},5843:function(e,t,n){"use strict";n("99af"),n("4de4"),n("c975"),n("a434"),n("b0c0");var r=n("c0d6");function o(e){var t=(r["a"].getters.project||{}).steps||[],n=t.filter((function(t){return t.name===e}));return n.length>0?n[0]:null}function a(){var e=(r["a"].getters.project||{}).steps||[],t=e.filter((function(e){return e.status.selected}));return t.length>0?t[0]:null}function s(e){return r["a"].getters.queuedStepsToRun.filter((function(t){return t===e})).length>0}function i(e){var t=o(e);return null!==t&&t.status.running}function c(e){if(!s(e)&&!i(e)){var t=r["a"].getters.queuedStepsToRun.concat([e]);r["a"].commit("queuedStepsToRun",t)}}function u(e){var t=r["a"].getters.queuedStepsToRun.concat(),n=t.indexOf(e);return!(n<0)&&(t.splice(n,1),r["a"].commit("queuedStepsToRun",t),!0)}function l(e){var t=r["a"].getters.queuedStepsToRun.concat(),n=e.filter((function(e){return t.indexOf(e)<0}));n.length>0&&r["a"].commit("queuedStepsToRun",t.concat(n))}function d(e){r["a"].commit("runningStepName",e),r["a"].commit("running",null!==e)}function p(){r["a"].commit("queuedStepsToRun",[])}t["a"]={addToQueue:l,clearQueue:p,getStep:o,getSelectedStep:a,isStepQueued:s,isStepRunning:i,queueStepToRun:c,removeStepFromQueue:u,setStepRunning:d}},"5c0b":function(e,t,n){"use strict";var r=n("9c0c"),o=n.n(r);o.a},"6f3f":function(e,t,n){},"726c":function(e,t,n){"use strict";n("99af"),n("4de4"),n("c975"),n("d81d");var r=n("c0d6"),o=["EXECUTION_ERROR"];function a(e){var t=r["a"].getters.errors.concat(),n=t.map((function(e){return e.code})).concat(o),a=(e||[]).filter((function(e){return-1===n.indexOf(e.code)}));a&&r["a"].commit("errors",t.concat(a))}function s(e){return a([e])}function i(e){var t=r["a"].getters.warnings.concat(),n=t.map((function(e){return e.code})),o=(e||[]).filter((function(e){return-1===n.indexOf(e.code)}));o&&r["a"].commit("warnings",t.concat(o))}function c(e){return i([e])}t["a"]={addErrors:a,addError:s,addWarnings:i,addWarning:c}},"771f":function(e,t,n){"use strict";var r=n("e95f"),o=n.n(r);o.a},"7d32":function(e,t,n){},"7e5d":function(e,t,n){},"82dc":function(e,t,n){"use strict";var r=n("6f3f"),o=n.n(r);o.a},8382:function(e,t,n){"use strict";var r=function(){var e=this,t=e.$createElement,n=e._self._c||t;return n("div",{staticClass:"Spinner"},[n("svg",{staticClass:"Spinner__box",attrs:{xmlns:"http://www.w3.org/2000/svg",width:e.size,height:e.size}},[n("circle",{staticClass:"Spinner__path",class:e.themingClasses,attrs:{fill:"none","stroke-linecap":"round","stroke-width":e.thickness,cx:e.half,cy:e.half,r:e.radius}})])])},o=[];n("a9e3");function a(){return this.size}function s(){return Math.floor(this.size/2)}function i(){return this.half-this.thickness}function c(){return Math.max(2,Math.floor(6*Math.min(1,this.size/60)))}function u(){return"Spinner__path--".concat(this.theme)}var l={name:"Spinner",props:{size:{type:Number,default:40},theme:{type:String,default:"light"}},computed:{extent:a,half:s,radius:i,thickness:c,themingClasses:u}},d=l,p=(n("e675"),n("2877")),f=Object(p["a"])(d,r,o,!1,null,"38b6b456",null);t["a"]=f.exports},"921b":function(e,t,n){},"9c0c":function(e,t,n){},b6ef:function(e,t,n){},ba6a:function(e,t,n){"use strict";n("4de4"),n("13d5"),n("fb6a"),n("b0c0"),n("d3b7"),n("ac1f"),n("1276"),n("96cf");var r=n("1da1"),o=n("bc3a"),a=n.n(o),s=n("c0d6"),i=n("5843"),c=n("3fa3"),u=n("726c"),l=n("025e"),d={lastInvocationTimestamp:0};function p(){s["a"].commit("isStatusDirty",!0)}function f(e){var t=((e||{}).data||{}).errors||[];u["a"].addErrors(t)}function v(e){var t=((e||{}).data||{}).warnings||[];u["a"].addWarnings(t)}function m(e){var t=window.location.origin;return a.a.create({baseURL:"".concat(t,"/v1/api/"),timeout:e||1e4,headers:{"Content-Type":"application/json"}})}function h(e,t){return m(t).get(e).catch((function(t){throw console.error("FAILED GET::".concat(e),t),t}))}function g(e,t,n){return m(n).post(e,t||{}).catch((function(n){throw console.error("FAILED POST::".concat(e),t,n),n}))}function _(e){var t=e.split(" ")[0];return g("/command/sync/".concat(t),{prefix:t,command:e},3e4).then((function(e){return f(e),v(e),e}))}function y(e){var t=e.split(" ")[0];return g("/command/async/".concat(t),{prefix:t,command:e}).then((function(e){return f(e),v(e),e}))}function C(e){var t=e.data.data.step_changes||[],n=!e.data.success||(e.data.errors||[]).length>0||t.filter((function(e){return((e||{}).step||{}).has_error})).length>0;return n&&(i["a"].clearQueue(),s["a"].commit("running",!1),p()),n}function b(e){return s["a"].commit("running",!0),s["a"].commit("runningStepName",e),y('run "'.concat(e,'" --print-status'),e).then((function(e){C(e);var t=e.data;return c["a"].applyStepModifications(t.data.step_renames,t.data.step_changes).then((function(){return p(),e}))}))}function w(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:0,t=arguments.length>1&&void 0!==arguments[1]&&arguments[1],n=Math.max(d.lastInvocationTimestamp,0);if(e>0){var r=(new Date).getTime(),o=r-n;if(o<e)return Promise.resolve({data:s["a"].getters.status})}var a=t?"yes":null,i=(s["a"].getters.status||{}).timestamp||0,u={last_timestamp:i,force:a};return d.lastInvocationTimestamp=(new Date).getTime(),g("/status",u).then((function(e){var t=e.data;if(!t)return Promise.resolve(e);t.success||(d.lastInvocationTimestamp=0);var n=t.data,r=n.project,o=n.remote,a=t.data.is_active_async,i=(r||{}).steps||[],u=C(e),f=(s["a"].getters.status||{}).hash||"",v=t.hash||"",m=i.filter((function(e){return e.status.running})),h=!u&&m.length>0,g=((o||{}).sync||{}).active;f!==v&&(s["a"].commit("status",t),s["a"].commit("project",r));var _=s["a"].getters.running,y=g||h||a||s["a"].getters.queuedStepsToRun.length>0;_!==y&&s["a"].commit("running",y);var w=s["a"].getters.runningStepName,S=[h?m[0].name:null,y?w:null],O=S.reduce((function(e,t){return t||e}),null);return w!==O&&s["a"].commit("runningStepName",O),_&&!y&&p(),c["a"].applyStepModifications(t.data.step_renames,t.data.step_changes).then((function(){var t=!g&&!h&&!a&&s["a"].getters.queuedStepsToRun.length>0;if(t){var n=s["a"].getters.queuedStepsToRun[0];return s["a"].commit("queuedStepsToRun",s["a"].getters.queuedStepsToRun.slice(1)),l["a"].thenWait(100).then((function(){return b(n)})).then((function(){return l["a"].thenWait(100)})).then((function(){return e}))}return e}))}))}function S(){return O.apply(this,arguments)}function O(){return O=Object(r["a"])(regeneratorRuntime.mark((function e(){var t;return regeneratorRuntime.wrap((function(e){while(1)switch(e.prev=e.next){case 0:return i["a"].clearQueue(),e.next=3,g("/command/abort");case 3:return t=e.sent,f(t),v(t),s["a"].commit("running",!1),p(),e.abrupt("return",t);case 9:case"end":return e.stop()}}),e)}))),O.apply(this,arguments)}t["a"]={abortExecution:S,get:h,post:g,execute:_,executeAsync:y,updateStatus:w,markStatusDirty:p}},c0d6:function(e,t,n){"use strict";var r=n("a026"),o=n("2f62");function a(){return{data:{success:!0,timestamp:0}}}r["a"].use(o["a"]),t["a"]=new o["a"].Store({state:{followSteps:!0,errors:[],warnings:[],isStatusDirty:!0,project:null,queuedStepsToRun:[],running:!1,runningStepName:null,savingFile:!1,status:a(),loadingMessages:[],isNotebookLoading:!1,previousStepChanges:{}},mutations:{followSteps:function(e,t){e.followSteps=t||!1},errors:function(e,t){e.errors=t||[]},warnings:function(e,t){e.warnings=t||[]},isStatusDirty:function(e,t){e.isStatusDirty=t||!1},project:function(e,t){e.project=t||null},queuedStepsToRun:function(e,t){e.queuedStepsToRun=t||[]},running:function(e,t){e.running=t||!1},runningStepName:function(e,t){e.runningStepName=t||null},savingFile:function(e,t){e.savingFile=t||!1},status:function(e,t){e.status=t||a()},loadingMessages:function(e,t){e.loadingMessages=t||[]},isNotebookLoading:function(e,t){e.isNotebookLoading=t||!1},previousStepChanges:function(e,t){e.previousStepChanges=t||{}}},getters:{followSteps:function(e){return e.followSteps},errors:function(e){return e.errors},warnings:function(e){return e.warnings},isStatusDirty:function(e){return e.isStatusDirty},project:function(e){return e.project},queuedStepsToRun:function(e){return e.queuedStepsToRun},running:function(e){return e.running},runningStepName:function(e){return e.runningStepName},savingFile:function(e){return e.savingFile},status:function(e){return e.status},view:function(e){return((e.status||{}).data||{}).view||null},loadingMessages:function(e){return e.loadingMessages},isNotebookLoading:function(e){return e.isNotebookLoading},previousStepChanges:function(e){return e.previousStepChanges}}})},c3b6:function(e,t,n){"use strict";var r=n("04e4"),o=n.n(r);o.a},e675:function(e,t,n){"use strict";var r=n("921b"),o=n.n(r);o.a},e95f:function(e,t,n){},ea2f:function(e,t,n){"use strict";var r=function(){var e=this,t=e.$createElement,n=e._self._c||t;return n("div",{staticClass:"Loader"},[n("div",{staticClass:"Loader__focus"},[n("spinner",{staticClass:"Loader__spinner"}),e.message?n("div",{staticClass:"Loader__message"},[e._v(e._s(e.message))]):e._e()],1)])},o=[],a=n("8382");function s(){return{}}var i={name:"Loader",components:{Spinner:a["a"]},props:{message:{type:String,default:""}},data:s},c=i,u=(n("1aaf"),n("2877")),l=Object(u["a"])(c,r,o,!1,null,"d43f3f76",null);t["a"]=l.exports},ff27:function(e,t,n){"use strict";var r=n("b6ef"),o=n.n(r);o.a}});
//# sourceMappingURL=app.cf0a4552.js.map