<template lang="pug">
  .ProjectMenuOverlay
    menu-button(icon="refresh" label="Refresh Notebook Display" @click="refreshDisplay")
    menu-button(icon="folder" label="Explore Directory" @click="openDirectory")
    menu-button(icon="save_alt" label="Save As Reader File" @click="saveReaderFile")
    .ProjectMenuOverlay__separator
    menu-button(icon="close" label="Close Project" @click="closeProject")
</template>

<script>
import MenuButton from './MenuButton.vue';
import emitter from '../../../emitter';
import http from '../../../http';

function refreshDisplay() {
  this.show = false;
  emitter.$emit('refresh-notebook');
}

function saveReaderFile() {
  this.show = false;
  this.$store.commit('savingFile', true);
}

function openDirectory() {
  this.show = false;
  return http.execute('show files');
}

function data() {
  return {
    show: false,
  };
}

function closeProject() {
  this.$emit('action', { action: 'close-project' });
}

export default {
  name: 'ProjectMenuOverlay',
  components: { MenuButton },
  data,
  methods: {
    closeProject,
    openDirectory,
    refreshDisplay,
    saveReaderFile,
  },
};
</script>

<style scoped lang="scss">
  .ProjectMenuOverlay {

    &__row {
      display: flex;
      align-items: center;
    }

    &__spacer {
      flex: 1;
    }

    &__separator {
      height: 1px;
      width: 100%;
      margin: 0.1em 0;
      background-color: rgba(0, 0, 0, 0.1);
    }
  }
</style>
