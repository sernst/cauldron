<template lang="pug">
  #app.App
    router-view.App__routerView
    warning-overlay(v-if="warning" :warning="warning" @close="onDismissWarning")
    error-overlay(v-if="error" :error="error" @close="onDismissError")
    lost-connection-overlay(v-if="showLostConnection")
    loader(v-if="loadingMessage.id", :message="loadingMessage.message")
</template>

<script>
import http from './http';
import WarningOverlay from './components/warningOverlay/WarningOverlay.vue';
import ErrorOverlay from './components/errorOverlay/ErrorOverlay.vue';
import exceptions from './exceptions';
import LostConnectionOverlay from './components/lostConnectionOverlay/LostConnectionOverlay.vue';
import utils from './utils';
import Loader from './components/loader/Loader.vue';

const SUCCESS = 'success';
const FAILED = 'failure';
const LOST = 'lost';

function loadingMessage() {
  const items = this.$store.getters.loading || [];
  return items.length > 0 ? items.splice(-1)[0] : {};
}

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

/**
 *
 */
function onDismissError() {
  const errors = this.$store.getters.errors.concat();

  if (errors.length < 1) {
    return;
  }

  errors.shift();
  this.$store.commit('errors', errors);
}

function recordResponse(kind, responseOrError) {
  this.recentResponses.push({ kind, responseOrError, success: kind === SUCCESS });
  if (this.recentResponses.length > 50) {
    this.recentResponses.shift();
  }
  return responseOrError;
}

function updateStatusLoop() {
  const { isStatusDirty, isNotebookLoading } = this.$store.getters;

  if (isStatusDirty) {
    this.$store.commit('isStatusDirty', false);
  }

  // If the notebook display is in the process of loading, don't update status
  // as that just competes with the notebook loading process and UI state
  // can't change while the notebook display is loading anyway.
  if (isNotebookLoading) {
    clearTimeout(this.timeoutHandle);
    this.timeoutHandle = setTimeout(this.updateStatusLoop, 200);
    return Promise.resolve();
  }

  const debounce = this.$store.getters.running ? 500 : 1000;
  return http.updateStatus(isStatusDirty ? 0 : debounce)
    .then((response) => {
      if (response.data.success) {
        this.recordResponse(SUCCESS, response);
        return response;
      }

      const codes = response.data.errors.map(e => e.code);
      if (codes.indexOf('LOST_REMOTE_CONNECTION') !== -1) {
        return this.recordResponse(LOST, response);
      }

      this.recordResponse(FAILED, response);
      console.error('Failed update response', response.data);
      return response;
    })
    .catch((e) => {
      // https://github.com/axios/axios#handling-errors
      if (!e.request) {
        this.recordResponse(FAILED, e);
        exceptions.addError({
          code: 'UNKNOWN_ERROR',
          message: 'Malformed request attempt has halted communication with the kernel.',
        });
        console.warn(e);
        return Promise.resolve();
      }

      if (e.code === 'ECONNABORTED' || (e.response || {}).status === 408) {
        this.recordResponse(LOST, e);
        return utils.thenWait(200);
      }

      if (!e.response) {
        this.recordResponse(LOST, e);
        return utils.thenWait(500);
      }

      this.recordResponse(FAILED, e);
      return utils.thenWait(200);
    })
    .finally(() => {
      const { path } = this.$router.currentRoute;
      const { project, view } = this.$store.getters;

      if (view && !path.startsWith('/view')) {
        // Go to the view screen if a reader file is loaded and not in a view route.
        this.$router.push('/view');
      } else if (!view && project && !path.startsWith('/project')) {
        // Go to the project screen if a project is loaded and not in a project route.
        this.$router.push('/project');
      } else if (project === null && path.startsWith('/project')) {
        // Go home on reload if there is no open project.
        this.$router.push('/');
      } else if (view === null && path.startsWith('/view')) {
        // Go home on reload if there is no open view.
        this.$router.push('/');
      }

      clearTimeout(this.timeoutHandle);
      this.timeoutHandle = setTimeout(this.updateStatusLoop, 100);
    });
}

function showLostConnection() {
  if (this.recentResponses.length === 0) {
    return false;
  }
  const lastResponseKind = this.recentResponses.slice(-1)[0].kind;
  return (lastResponseKind === LOST);
}

function data() {
  return {
    timeoutHandle: null,
    recentResponses: [],
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
  components: {
    Loader,
    LostConnectionOverlay,
    ErrorOverlay,
    WarningOverlay,
  },
  data,
  computed: {
    warning,
    error,
    showLostConnection,
    loadingMessage,
  },
  mounted,
  beforeDestroy,
  methods: {
    recordResponse,
    updateStatusLoop,
    onDismissWarning,
    onDismissError,
  },
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
