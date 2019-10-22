<template lang="pug">
    .Project
      menu-strip.Project__menuStrip(@close-project="closeProject")
      .Project__verticalSeparator
      run-strip.Project__runStrip(
        @aborting="onAbortingRun"
        @aborted="onAbortedRun"
        @settings="onEditStepSettings"
      )
      .Project__verticalSeparator
      notebook(@loaded="onNotebookLoaded")

      step-settings-modal(v-if="stepToEdit" :step="stepToEdit" @close="onStepSettingsChange")
      saver(v-if="$store.getters.savingFile")
      loader(v-if="loadingDisplayMessage" :message="loadingDisplayMessage")
</template>

<script>
import http from '../../http';
import Loader from '../../components/loader/Loader.vue';
import RunStrip from './RunStrip/RunStrip.vue';
import MenuStrip from './MenuStrip/MenuStrip.vue';
import Notebook from './Notebook/Notebook.vue';
import StepSettingsModal from './StepSettingsModal/StepSettingsModal.vue';
import Saver from '../../components/saver/Saver.vue';

function loadingDisplayMessage() {
  if (this.loadingMessage) {
    return this.loadingMessage;
  }

  const sync = (((this.$store.getters.status || {}).data || {}).remote || {}).sync || {};
  if (sync.active) {
    return 'Synchronizing local files to remote kernel';
  }

  return null;
}

/**
 * Closes the currently opened project and returns to the home screen.
 */
function closeProject() {
  document.title = 'Cauldron';
  this.loadingMessage = 'Closing Project';
  return http.execute('close')
    .then(() => this.$router.push('/'));
}

function onAbortingRun(event) {
  this.loadingMessage = `Aborting "${event.step.name}" Execution`;
}

function onAbortedRun() {
  this.loadingMessage = null;
}

function onNotebookLoaded(event) {
  this.loadingMessage = event.value ? null : 'Refreshing notebook';
}

function onStepSettingsChange() {
  this.stepToEdit = null;
}

function onEditStepSettings(event) {
  this.stepToEdit = event.step;
}

function data() {
  return {
    loadingMessage: null,
    stepToEdit: null,
  };
}

function mounted() {
  const existingProject = this.$store.getters.project;
  if (existingProject) {
    document.title = existingProject.title;
    return Promise.resolve();
  }

  this.loadingMessage = 'Establishing project state.';
  return http.updateStatus()
    .then(() => {
      const { project } = this.$store.getters;
      document.title = project.title;

      this.loadingMessage = 'Initializing project display';
      // Waits for a notebook loaded event to hide this message.
    });
}

export default {
  name: 'Project',
  components: {
    StepSettingsModal,
    Notebook,
    Loader,
    MenuStrip,
    RunStrip,
    Saver,
  },
  data,
  computed: { loadingDisplayMessage },
  mounted,
  methods: {
    closeProject,
    onNotebookLoaded,
    onAbortingRun,
    onAbortedRun,
    onStepSettingsChange,
    onEditStepSettings,
  },
};
</script>

<style scoped lang="scss">
  .Project {
    display: flex;
    background-color: white;

    &__verticalSeparator {
      width: 1px;
      height: 100%;
      background-color: #DDD;
    }
  }
</style>
