<template lang="pug">
    .Create
      .Create__form
        .Create__titleBox
          .Create__title Create New Notebook

        .Create__textInput
          input.Create__name.input.is-small(
            placeholder="Notebook Name"
            type="text"
            v-model:value="name"
          )
          .Create__info
            | This will also be the name of the folder created for the notebook.
        .Create__checkbox
          label.checkbox
            input(type="checkbox" v-model:value="autoName")
            span.Create__checkboxLabel Automatic Step Prefixes
          .Create__info
            | Adds a prefix of "S##-" to steps to reflect their order within the project.
            | Automatically updates prefixes when step ordering changes to reflect the changed
            | ordering.
        .Create__checkbox
          label.checkbox
            input(type="checkbox" v-model:value="addLibraryDirectory")
            span.Create__checkboxLabel Create Library "libs" Folder
          .Create__info
            | Adds a "libs" folder for local library development within your notebook.
        .Create__checkbox
          label.checkbox
            input(type="checkbox" v-model:value="addAssetsDirectory")
            span.Create__checkboxLabel Create Assets Folder
          .Create__info
            | Create an "assets" folder to store images and other media that need to be included
            | in the displayed results.
        .Create__buttonBox
          button.button.is-small.is-success(
            @click="onCreate"
            :disabled="!allowCreate"
          ) Create Project
      .Create__locationBox
        .Create__locationHeaderBox
          .Create__locationTitle Parent Directory
          .Create__locationSubtitle
            | The parent directory in which your notebook folder will be created.
        browser(:location="location" @select="onSelectFolder" :show-files="false")

      alert-dialog(
        v-if="alterMessage"
        :message="alertMessage.message"
        :title="alertMessage.title"
        :ok-label="alertMessage.buttonLabel"
        @ok="onDismissAlert"
      )
</template>

<script>
import Browser from '../../components/browser/Browser.vue';
import AlertDialog from '../../components/alertDialog/AlertDialog.vue';
import http from '../../http';

function onDismissAlert() {
  this.alertMessage = null;
}

function onSelectFolder(event) {
  const { spec } = event.value;
  if (spec) {
    this.alertMessage = {
      title: 'Not Allowed',
      message: 'Cannot create notebooks within other notebook folders.',
    };
    return Promise.resolve();
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

function onCreate() {
  const elements = [
    'create',
    `"${this.name}"`,
    `"${this.location.current_directory}"`,
    `--title="${this.name}"`,
    this.autoName ? null : '--no-naming-scheme',
    this.addLibraryDirectory ? '--libs=libs' : null,
    this.addAssetsDirectory ? '--assets=assets' : null,
  ];
  const command = elements.filter(e => e).join(' ');

  console.log('Creating project', command);
  this.loadingMessage = `Creating your "${this.name}" project`;
  return http.execute(command).then(() => http.markStatusDirty());
}

function data() {
  return {
    loadingMessage: 'Synchronizing with kernel',
    location: {},
    name: null,
    autoName: true,
    addLibraryDirectory: false,
    addAssetsDirectory: false,
    alertMessage: null,
  };
}

function mounted() {
  return http.execute('ls')
    .then((response) => {
      this.location = response.data.data;
      this.loadingMessage = null;
    });
}

function allowCreate() {
  return this.name && this.name.length > 0;
}

export default {
  name: 'Create',
  components: { AlertDialog, Browser },
  data,
  computed: { allowCreate },
  mounted,
  methods: { onSelectFolder, onCreate, onDismissAlert },
};
</script>

<style scoped lang="scss">
  .Create {
    font-family: "Source Sans Pro", sans-serif;
    display: flex;

    &__form {
      flex: 1;
      height: 100%;
      overflow: hidden;
      padding: 0 1em 2em 1em;
    }

    &__locationBox {
      flex: 1;
      display: grid;
      padding: 1em;
      grid-template-columns: repeat(1, 1fr);
      grid-template-rows: min-content 1fr;
    }

    &__locationHeaderBox {
      margin-bottom: 1em;
      grid-row: 1;
      grid-column: 1;
    }

    &__locationSubtitle {
      font-size: 0.6em;
      color: #999;
      grid-row: 2;
      grid-column: 1;
    }

    &__checkbox {
      margin: 1em 0;
      user-select: none;
    }

    &__checkboxLabel {
      margin-left: 0.25em;
    }

    &__info {
      padding-left: 2em;
      font-size: 0.6em;
      color: #999;
    }

    &__titleBox {
      margin: 1em 0 2em 0;
    }

    &__title {
      font-size: 1.2em;
    }

    &__buttonBox {
      margin-top: 1em;
      display: flex;
      justify-content: flex-end;
    }
  }
</style>
