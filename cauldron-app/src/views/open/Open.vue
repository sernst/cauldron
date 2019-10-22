<template lang="pug">
    .Open
      .Open__browser
        .Open__titleBox
          .Open__title Open Existing Notebook
        browser.Open__browserBox(:location="location" @select="onSelectFolder")
      // The known section is a vertical list of known projects that
      // can quickly be selected and opened.
      .Open__known(v-if="availableProjects")
        .Open__goup(v-for="(items, root) in availableProjects")
          project-item-group(
            :root="root"
            :items="items"
            @open="onProjectClick"
          )

      loader(v-if="loadingMessage" :message="loadingMessage")
</template>

<script>
import Loader from '../../components/loader/Loader.vue';
import http from '../../http';
import ProjectItemGroup from './ProjectItemGroup.vue';
import Browser from '../../components/browser/Browser.vue';

/**
 * Opens the project specified by the event.
 * @param event
 */
function onProjectClick(event) {
  const { name } = event.item;
  const directory = event.item.directory.absolute;

  this.loadingMessage = `Loading "${name}" Project`;
  return http.execute(`open "${directory}"`)
    .then((response) => {
      http.markStatusDirty();

      if (!response.data.success) {
        this.loadingMessage = null;
      }
    });
}

function onSelectFolder(event) {
  if (event.type === 'file') {
    return Promise.resolve();
  }

  const { spec } = event.value;
  if (spec) {
    return this.onProjectClick({ item: spec });
  }

  this.loadingMessage = 'Opening selected directory';
  return http.execute(`cd "${event.value.directory}"`)
    .then((response) => {
      this.loadingMessage = null;
      if (response.data.success) {
        this.location = response.data.data;
      }
    });
}

function data() {
  return {
    loadingMessage: 'Fetching available projects',
    availableProjects: {},
    location: {},
  };
}

function mounted() {
  const listingPromise = http.execute('list all')
    .then((response) => {
      this.availableProjects = response.data.data.spec_groups;
    });

  const directoryPromise = http.execute('ls')
    .then((response) => {
      this.location = response.data.data;
    });

  return Promise.all([listingPromise, directoryPromise])
    .then(() => {
      this.loadingMessage = null;
    });
}

export default {
  name: 'Open',
  components: { Browser, ProjectItemGroup, Loader },
  data,
  mounted,
  methods: { onProjectClick, onSelectFolder },
};
</script>

<style scoped lang="scss">
  .Open {
    display: flex;

    &__browser {
      flex: 3;
      overflow: hidden;
      /*height: 100%;*/
      padding: 0 1em 3em 1em;
      display: grid;
      /*padding: 1em;*/
      grid-template-columns: repeat(1, 1fr);
      grid-template-rows: min-content 1fr;
    }

    &__known {
      flex: 2;
      min-width: 320px;
      max-width: 580px;
      padding: 0.5em 0 20em 0;
      overflow-y: scroll;
    }

    &__titleBox {
      margin: 1em 0 2em 0;
      grid-row: 1;
      grid-column: 1;
    }

    &__title {
      font-size: 1.2em;
    }

    &__browserBox {
      grid-row: 2;
      grid-column: 1;
    }
  }
</style>
