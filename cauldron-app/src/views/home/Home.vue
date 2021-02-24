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
          .Home__version
            .Home__versionPrefix Kernel:
            .Home__versionValue(:class="versionClasses") v{{ info.version }}
            .Home__versionPrefix Python:
            .Home__versionValue(:class="pythonVersionClasses") v{{ info.python_version }}
          .Home__version
            .Home__versionPrefix Server:
            .Home__versionValue(:class="versionClasses") v{{ info.ui_server_version }}
            .Home__versionPrefix Python:
            .Home__versionValue(:class="pythonVersionClasses") v{{ info.ui_python_version }}
          .Home__version
            .Home__versionPrefix Web:
            .Home__versionValue v{{ uiVersion }}
            .Home__versionPrefix Notebook:
            .Home__versionValue {{ info.notebook_version }}
        .Home__buttonBox
          .button.Home__button.tooltip(
            data-tooltip="A new notebook project"
            @click="createProject"
          ) Create
          .button.Home__button.tooltip(
            data-tooltip="An existing notebook project from a local directory"
            @click="openProjectBrowser"
          ) Open

      // Floating buttons
      remote-connect.Home__remoteConnect(:status="info")

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
import utils from '@/utils';
import Loader from '@/components/loader/Loader.vue';
import http from '@/http';
import logo from './logo-128.png';
import RecentItem from './RecentItem.vue';
import RemoteConnect from './RemoteConnect.vue';

/**
 * Returns the web GUI application version that was built into the JS from
 * package.json at build time for display.
 */
function uiVersion() {
  return utils.getBuildVar('UI_VERSION') || '???';
}

/**
 * Returns dynamic classes to style the Cauldron version values in the
 * display. Normally no classes will be returned, but if the major and/or
 * minor versions are different between the UI server and the kernel, a
 * danger class will be included. If the micro/patch version are different
 * a warning class will be returned.
 */
function versionClasses() {
  try {
    const parts = this.info.version.split('.');
    const uiParts = this.info.ui_server_version.split('.');
    if (parts[0] !== uiParts[0] || parts[1] !== uiParts[1]) {
      return ['Home__versionValue--danger'];
    }
    if (parts[2] !== uiParts[2]) {
      return ['Home__versionValue--warning'];
    }
    return [];
  } catch (_) {
    return [];
  }
}

/**
 * Returns dynamic classes to style the Python version values in the
 * display. Normally no classes will be returned, but if the major and/or
 * minor versions are different between the UI server and the kernel, a
 * danger class will be included. If the micro/patch version are different
 * a warning class will be returned.
 */
function pythonVersionClasses() {
  try {
    const parts = this.info.python_version.split('.');
    const uiParts = this.info.ui_python_version.split('.');
    if (parts[0] !== uiParts[0] || parts[1] !== uiParts[1]) {
      return ['Home__versionValue--danger'];
    }
    if (parts[2] !== uiParts[2]) {
      return ['Home__versionValue--warning'];
    }
    return [];
  } catch (_) {
    return [];
  }
}

/**
 * The create button routes to the create view.
 */
function createProject() {
  return this.$router.push('/create');
}

/**
 * the open button routes to the open project view.
 */
function openProjectBrowser() {
  return this.$router.push('/open');
}

/**
 * Opens the project specified by the event.
 * @param event
 */
async function onProjectClick(event) {
  const { uid } = event.item;
  if (event.action === 'remove') {
    this.loadingMessage = 'Removing Recent Project Entry';
    const response = await http.execute(`list erase ${uid} --yes`);
    this.recentProjects = response.data.data.projects;
    this.loadingMessage = null;
    return;
  }

  const { name } = event.item;
  const directory = event.item.directory.absolute;
  this.loadingMessage = `Loading "${name}" Project`;
  const response = await http.execute(`open "${directory}"`);
  http.markStatusDirty();
  if (!response.data.success) {
    this.loadingMessage = null;
  }
}

function data() {
  return {
    logo,
    loadingMessage: 'Synchronizing with Cauldron Kernel',
    // Placeholder value until the mount has retrieved the info from the UI server.
    info: {
      notebook_version: 'v0',
      version: '0.0.0',
      ui_server_version: '0.0.0',
      python_version: '0.0.0',
      ui_python_version: '0.0.0',
    },
    recentProjects: [],
  };
}

async function mounted() {
  const updateResponse = await http.updateStatus(500);
  this.info = updateResponse.data.data;

  const recentResponse = await http.execute('list recent');
  this.recentProjects = recentResponse.data.data.projects;
  this.loadingMessage = null;
}

export default {
  name: 'Home',
  components: { Loader, RecentItem, RemoteConnect },
  data,
  computed: { uiVersion, versionClasses, pythonVersionClasses },
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
      width: 100%;
      display: flex;
      justify-content: flex-end;
      margin: 0.25em 0;
    }

    &__versionValue {
      min-width: 30px;
      text-align: right;

      &--danger {
        font-weight: bold;
        color: #d65150;
      }

      &--warning {
        font-weight: bold;
        color: #d69c44;
      }
    }

    &__versionPrefix {
      min-width: 50px;
      opacity: 0.6;
      margin: 0 0.5em;
      text-align: right;
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
