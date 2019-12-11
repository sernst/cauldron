import Vue from 'vue';
import VueTippy, { TippyComponent } from 'vue-tippy';

import App from './App.vue';
import router from './router';
import store from './store';

Vue.use(VueTippy);
Vue.component('tippy', TippyComponent);

Vue.config.productionTip = false;

new Vue({
  router,
  store,
  render: h => h(App),
}).$mount('#app');
