<template lang="pug">
  .Home

    // The splash screen is the primary portion of the home screen that
    // contains the Cauldron brancing along with key navigation elements.
    .Home__splash
      .Home__focus
        img.Home__logo(:src="logo")
        .Home__title Cauldron
        .Home__tagline
          div Interactive Computing Environment
          div.Home__version v{{ info.version }}
        .Home__buttonBox
          .button.Home__button.tooltip(
            data-tooltip="A new notebook project"
            @click.stop="createProject"
          ) Create
          .button.Home__button.tooltip(
            data-tooltip="An existing notebook project from a local directory"
            @click.stop="openProjectBrowser"
          ) Open

      // Floating buttons
      // remote-connect.Home__remoteConnect(:status="info")

    // The recent section is a vertical list of recently opened projects that
    // can quickly be selected and reopened.
    .Home__recent(v-if="recentProjects.length > 0")
      recent-item(
        v-for="item in recentProjects"
        :item="item"
        @click="onProjectClick"
      )

    loader(v-if="loadingMessage" :message="loadingMessage")
</template>

<script>
import logo from './logo-128.png';
import Loader from '../../components/loader/Loader.vue';
import RecentItem from './RecentItem.vue';
import RemoteConnect from './RemoteConnect.vue';
import http from '../../http';

/**
 * The create button routes to the create view.
 */
function createProject() {
  return this.$router.push('/create');
}

function openProjectBrowser() {
  return this.$router.push('/open');
}

/**
 * Opens the project specified by the event.
 * @param event
 */
function onProjectClick(event) {
  const { uid } = event.item;
  if (event.action === 'remove') {
    this.loadingMessage = 'Removing Recent Project Entry';
    return http.execute(`list erase ${uid} --yes`)
      .then((response) => {
        this.recentProjects = response.data.data.projects;
        this.loadingMessage = null;
      });
  }

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

function data() {
  return {
    logo,
    loadingMessage: 'Synchronizing with Cauldron Kernel',
    info: { version: 'unknown' },
    recentProjects: [],
  };
}

function mounted() {
  return http.updateStatus(500)
    .then((response) => {
      this.info = response.data.data;
      return http.execute('list recent');
    })
    .then((response) => {
      this.recentProjects = response.data.data.projects;
      this.loadingMessage = null;
    });
}

export default {
  name: 'Home',
  components: { Loader, RecentItem, RemoteConnect },
  data,
  mounted,
  methods: { createProject, onProjectClick, openProjectBrowser },
};
</script>

<style scoped lang="scss">
  @import '../../Variables';

  .Home {
    font-family: "Source Sans Pro", sans-serif;
    display: flex;

    &__splash {
      display: flex;
      flex: 3;
      align-items: center;
      justify-content: center;
    }

    &__recent {
      flex: 2;
      min-width: 320px;
      max-width: 580px;
      padding: 0.5em 0 20em 0;
      overflow-y: scroll;
    }

    &__focus {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      width: 50%;
      max-width: 480px;
    }

    &__logo {
      width: 48px;
      height: 48px;
    }

    &__title {
      padding-top: 0.2em;
      font-size: 2em;
      font-weight: lighter;
    }

    &__tagline {
      font-size: 0.8em;
    }

    &__version {
      font-size: 0.8em;
      text-align: right;
      width: 100%;
    }

    &__button {
      margin: 0.5em 0.25em;
    }

    &__remoteConnect {
      position: absolute;
      z-index: $overlay-z-index;
      bottom: 3em;
      left: 3em;
    }
  }
</style>
