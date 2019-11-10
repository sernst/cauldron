import Vue from 'vue';
import Router from 'vue-router';
import Home from './views/home/Home.vue';

Vue.use(Router);

export default new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home,
    },
    {
      path: '/project',
      name: 'project',
      component: () => import(/* webpackChunkName: "project" */ './views/project/Project.vue'),
    },
    {
      path: '/create',
      name: 'create',
      component: () => import(/* webpackChunkName: "create" */ './views/create/Create.vue'),
    },
    {
      path: '/open',
      name: 'open',
      component: () => import(/* webpackChunkName: "create" */ './views/open/Open.vue'),
    },
    {
      path: '/view',
      name: 'viewer',
      component: () => import(/* webpackChunkName: "create" */ './views/viewer/Viewer.vue'),
    },
  ],
});
