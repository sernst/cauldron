<template lang="pug">
  .Notebook
    iframe.Notebook__frame(v-if="showIframe" :src="notebookUrl")
</template>

<script>
import notebook from '../../notebook';
import emitter from '../../emitter';
import http from '../../http';

function showIframe() {
  const { project, view } = this.$store.getters;
  return (this.viewer ? view : project) !== null;
}

/**
 * The URL to load as part of displaying the project.
 */
function notebookUrl() {
  return this.viewer ? notebook.getViewUrl() : notebook.getUrl();
}

function selectedStep() {
  const { steps } = this.$store.getters.project || {};
  return (steps || []).reduce((acc, step) => {
    const match = step.status.selected ? step.name : null;
    return acc || match;
  }, null);
}

function watchSelectedStep(newStepName, oldStepName) {
  if (newStepName !== null && newStepName !== oldStepName) {
    notebook.scrollToStep(newStepName);
  }
}

function data() {
  return {
    isLoading: true,
  };
}

function refresh() {
  this.isLoading = true;
  this.$store.commit('isNotebookLoading', true);
  this.$emit('loaded', { value: false, source: 'Notebook.refresh' });
  notebook.refresh();
  return this.onLoaded();
}

/**
 * This function isn't currently used anywhere, but remains as a computed variable
 * because it is useful when debugging with the Vue panel.
 * @returns {*|boolean}
 */
function isInitialized() {
  const cauldron = notebook.getCauldronObject();
  return (cauldron && cauldron.on && cauldron.on.ready && true);
}

/**
 * This function isn't currently used anywhere, but remains as a computed variable
 * because it is useful when debugging with the Vue panel.
 * @returns {*|boolean}
 */
function isRunning() {
  const cauldron = notebook.getCauldronObject() || {};
  return cauldron.RUNNING || false;
}

function onLoaded() {
  return notebook.onLoaded()
    .then(() => {
      this.isLoading = false;
      this.$store.commit('isNotebookLoading', false);
      this.$emit('loaded', { value: true, source: 'Notebook.onLoaded' });
      http.markStatusDirty();
    })
    // Ignore errors caused by loading delays.
    .catch(() => null);
}

function mounted() {
  this.isLoading = true;
  this.$store.commit('isNotebookLoading', true);
  this.$emit('loaded', { value: false, source: 'Notebook.mounted' });

  // Don't return this promise because we don't want the resolution process to be
  // blocking.
  this.onLoaded()
    .then(() => {
      emitter.$on('refresh-notebook', this.refresh);
    })
    // Ignore errors caused by loading delays.
    .catch(() => null);
}

export default {
  name: 'Notebook',
  props: {
    viewer: { type: Boolean, default: false },
  },
  data,
  computed: {
    notebookUrl,
    selectedStep,
    isInitialized,
    isRunning,
    showIframe,
  },
  watch: { selectedStep: watchSelectedStep },
  mounted,
  methods: { onLoaded, refresh },
};
</script>

<style scoped lang="scss">
  @import '../../Variables';

  .Notebook {
    background-color: white;
    flex: 1;
    min-width: 480px;
    display: flex;
    position: relative;
    overflow: hidden;

    &__frame {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
    }

    &__overlay {
      font-family: "Source Sans Pro", sans-serif;
      font-size: 0.8em;
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: $overlay-z-index;
      background-color: white;
      padding-top: 4em;
      text-align: center;
    }
  }
</style>
