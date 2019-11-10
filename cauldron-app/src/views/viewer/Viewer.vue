<template lang="pug">
    .Viewer
      view-menu-strip(@close="closeViewer")
      notebook(@loaded="onNotebookLoaded" :viewer="true")
      loader(v-if="loadingMessage" :message="loadingMessage")
</template>

<script>
import http from '../../http';
import Loader from '../../components/loader/Loader.vue';
import Notebook from '../../components/Notebook/Notebook.vue';
import ViewMenuStrip from './ViewMenuStrip/ViewMenuStrip.vue';

/**
 * Closes the currently opened Viewer and returns to the home screen.
 */
function closeViewer() {
  document.title = 'Cauldron';
  this.loadingMessage = 'Closing Viewer';
  return http.execute('view close')
    .then(() => {
      this.$store.commit('isStatusDirty', true);
    });
}

function onNotebookLoaded(event) {
  this.loadingMessage = event.value ? null : 'Refreshing notebook';
}

function data() {
  return {
    loadingMessage: null,
  };
}

function mounted() {
  this.loadingMessage = 'Establishing Viewer state.';
  return http.updateStatus()
    .then(() => {
      const { view } = this.$store.getters;
      document.title = view.configs.title;

      this.loadingMessage = 'Initializing Viewer display';
      // Waits for a notebook loaded event to hide this message.
    });
}

export default {
  name: 'Viewer',
  components: { ViewMenuStrip, Notebook, Loader },
  data,
  mounted,
  methods: { closeViewer, onNotebookLoaded },
};
</script>

<style scoped lang="scss">
  .Viewer {
    display: flex;
    background-color: white;
  }
</style>
