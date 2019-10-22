<template lang="pug">
  #app.App
    router-view.App__routerView
    warning-overlay(v-if="warning" :warning="warning" @close="onDismissWarning")
    error-overlay(v-if="error" :error="error" @close="onDismissError")
    lost-connection-overlay(v-if="lostConnection")
</template>

<script>
import http from './http';
import WarningOverlay from './components/warningOverlay/WarningOverlay.vue';
import ErrorOverlay from './components/errorOverlay/ErrorOverlay.vue';
import exceptions from './exceptions';
import LostConnectionOverlay from './components/lostConnectionOverlay/LostConnectionOverlay.vue';
import utils from './utils';

function warning() {
  const { warnings } = this.$store.getters;
  return warnings.length < 1 ? null : warnings[0];
}

function onDismissWarning() {
  const warnings = this.$store.getters.warnings.concat();

  if (warnings.length < 1) {
    return;
  }

  warnings.shift();
  this.$store.commit('warnings', warnings);
}

function error() {
  const { errors } = this.$store.getters;
  return errors.length < 1 ? null : errors[0];
}

function onDismissError() {
  const errors = this.$store.getters.errors.concat();

  if (errors.length < 1) {
    return;
  }

  errors.shift();
  this.$store.commit('errors', errors);
}

function updateStatusLoop() {
  const { isStatusDirty } = this.$store.getters;

  if (isStatusDirty) {
    this.$store.commit('isStatusDirty', false);
  }

  const debounce = this.$store.getters.running ? 500 : 1000;
  return http.updateStatus(isStatusDirty ? 0 : debounce)
    .then((response) => {
      this.lostConnection = !response.data.data.version;

      if (!response.data.success) {
        console.error('Failed update response', response.data);
      }

      return response;
    })
    .catch((e) => {
      // https://github.com/axios/axios#handling-errors
      if (!e.request) {
        exceptions.addError({
          code: 'UNKNOWN_ERROR',
          message: 'Malformed request attempt made has halted communication with the kernel.',
        });
        console.warn(e);
        return Promise.resolve();
      }

      if (!e.response) {
        this.lostConnection = true;
        return utils.thenWait(1000);
      }

      this.lostConnection = false;
      console.error(e);
      return utils.thenWait(200);
    })
    .finally(() => {
      const { path } = this.$router.currentRoute;
      const { project } = this.$store.getters;

      if (project === null && path.startsWith('/project')) {
        // Go home on reload if there is no open project.
        this.$router.push('/');
      } else if (project && !path.startsWith('/project')) {
        // Go to the project screen if a project is loaded and not in a project route.
        this.$router.push('/project');
      }

      clearTimeout(this.timeoutHandle);
      this.timeoutHandle = setTimeout(this.updateStatusLoop, 100);
    });
}

function data() {
  return {
    lostConnection: false,
    timeoutHandle: null,
  };
}

function mounted() {
  return this.updateStatusLoop();
}

function beforeDestroy() {
  clearInterval(this.timeoutHandle);
}

export default {
  name: 'App',
  components: { LostConnectionOverlay, ErrorOverlay, WarningOverlay },
  data,
  computed: { warning, error },
  mounted,
  beforeDestroy,
  methods: { updateStatusLoop, onDismissWarning, onDismissError },
};
</script>

<style lang="scss">
  $material-icons-font-path: '~material-icons/iconfont/';
  @import '~material-icons/iconfont/material-icons.scss';
  @import "~source-sans-pro/source-sans-pro.css";
  @import "~bulma/css/bulma.css";
  @import "~bulma-extensions/dist/css/bulma-extensions.min.css";
  @import "App";
</style>
