<template lang="pug">
  .Notebook
    iframe.Notebook__frame(v-if="$store.getters.project" :src="notebookUrl")
</template>

<script>
import notebook from '../../../notebook';
import emitter from '../../../emitter';

/**
 * The URL to load as part of displaying the project.
 */
function notebookUrl() {
  return notebook.getUrl();
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
  this.$emit('loaded', { value: false });
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
      this.$emit('loaded', { value: true });
    });
}

function mounted() {
  this.$emit('loaded', { value: false });

  // Don't return this promise because we don't want the resolution process to be
  // blocking.
  this.onLoaded()
    .then(() => {
      emitter.$on('refresh-notebook', this.refresh);
    });
}

export default {
  name: 'Notebook',
  data,
  computed: {
    notebookUrl,
    selectedStep,
    isInitialized,
    isRunning,
  },
  watch: { selectedStep: watchSelectedStep },
  mounted,
  methods: { onLoaded, refresh },
};
</script>

<style scoped lang="scss">
  @import '../../../Variables';

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
