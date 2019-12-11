<template lang="pug">
  .Saver
    // Background modal dark overlay
    modal-scrim.Saver__scrim(:message="loadingMessage" @click="onDone")

    // Primary modal display
    .Saver__modal(v-if="location && !loadingMessage && !saveComplete && !confirmingOverwrite")
      .Saver__title Save Cauldron Notebook As...
      browser.Saver__browser(
        :location="location"
        :extra-locations="extraLocations"
        :extensions="['.cauldron']"
        @select="onBrowseSelected"
      )
      .Saver__inputBox
        input.Saver__input.input.is-small(type="text" placeholder="File Name" v-model="filename")
        button.Saver__button.button.is-small(@click="onDone") Cancel
        button.Saver__button.button.is-small.is-primary(@click="onSave(false)") Save

    alert-dialog(
      v-if="saveComplete"
      title="Save Complete"
      message="You're notebook has been successfully saved to"
      @ok="onDone"
    )
      .Saver__path {{ getOutputPath(true) }}

    confirm-dialog(
      v-if="confirmingOverwrite"
      title="Confirm Overwrite"
      message="Are you sure you want to overwrite the existing file?"
      @yes="onSave(true)"
      @no="confirmingOverwrite = false"
    )

</template>

<script>
import Browser from '../browser/Browser.vue';
import ModalScrim from '../modalScrim/ModalScrim.vue';
import http from '../../http';
import Spinner from '../spinner/Spinner.vue';
import AlertDialog from '../alertDialog/AlertDialog.vue';
import ConfirmDialog from '../confirmDialog/ConfirmDialog.vue';

/**
 * Called when the save process is aborted or when it is complete. This manages
 * the visibility of the save dialog from within the project view.
 */
function onDone() {
  this.$store.commit('savingFile', false);
}

/**
 * Executes the save action by calling the kernel to save out to the currently specified
 * directory with the currently specified filename.
 *
 * @param force
 *    Whether or not to force the saving action even if the output file already exists.
 *    When true, the file will be overwritten. When false, the save process will be
 *    aborted and a confirmation dialog shown to confirm the overwrite behavior.
 */
function onSave(force) {
  this.confirmingOverwrite = false;
  const filename = this.outputFilename;
  const exists = this.location.current_files.filter(f => f.name === filename).length > 0;

  console.log(exists, filename, this.location.current_files);

  if (!force && exists) {
    this.confirmingOverwrite = true;
    return Promise.resolve();
  }

  this.loadingMessage = `Saving notebook "${filename}"`;
  return http.execute(`save "${this.getOutputPath(false)}"`)
    .then(() => {
      this.loadingMessage = null;
      this.saveComplete = true;
    });
}

/**
 * Handles a selection event from the browser component. This will be the selection of a
 * folder or file.
 *
 * @param event
 *    The event that specifies the type of the selection and the value object that
 *    specifies it.
 */
function onBrowseSelected(event) {
  const { type } = event;

  if (type === 'file') {
    this.filename = event.value.name;
    return Promise.resolve();
  }

  return http.execute(`cd "${event.value.directory}"`)
    .then((response) => {
      if (response.data.success) {
        this.location = response.data.data;
      }
    });
}

function data() {
  return {
    // Project and other additional locations that should be available for quick
    // browsing. Initialized on mount.
    extraLocations: [],
    // Current browser location as specified by a kernel "ls" command.
    location: null,
    // Name of the file to be save, which will be updated at mount time and
    // editable by the user on input.
    filename: null,
    // When set, the modal scrum loading background will be displayed.
    loadingMessage: null,
    // Indicates the state of the dialog process such that the successful save
    // alert dialog is shown.
    saveComplete: false,
    // Indicates whether or not to show the overwrite existing reader file output
    // confirmation dialog.
    confirmingOverwrite: false,
  };
}

/**
 * Name of the file that will be saved when triggered. This includes adding the
 * .cauldron extension if not specified by the user.
 */
function outputFilename() {
  return this.filename.endsWith('.cauldron') ? this.filename : `${this.filename}.cauldron`;
}

/**
 * Returns the absolute output path where the reader file will be saved.
 *
 * @param short
 *    If true, the path will be shortened for display purposes only if the
 *    length of the path is longer than would fit comfortably in display
 *    elements.
 */
function getOutputPath(short) {
  const location = this.location || {};
  const prefix = short ? location.shortened_directory : location.current_directory;
  const separator = (prefix || '').includes('\\') ? '\\' : '/';
  return `${prefix || ''}${separator}${this.outputFilename}`;
}

/**
 * Initializes the display data and calls the `ls` Cauldron command in the kernel
 * to fetch the location information to display in the folder browser.
 */
function mounted() {
  const project = this.$store.getters.project || {};
  this.filename = `${project.title || 'unknown-project'}.cauldron`;

  const directory = project.remote_source_directory || project.source_directory;

  // Add project directory to the list of standard locations for browsing.
  this.extraLocations = [{ directory, label: 'Project Directory' }];

  return http.execute(`ls "${directory}"`)
    .then((response) => {
      this.location = response.data.data;
    });
}

export default {
  name: 'Saver',
  components: {
    ConfirmDialog,
    AlertDialog,
    ModalScrim,
    Browser,
    Spinner,
  },
  data,
  computed: { outputFilename },
  mounted,
  methods: {
    onDone,
    onSave,
    onBrowseSelected,
    getOutputPath,
  },
};
</script>

<style scoped lang="scss">
  @import '../../Variables';

  .Saver {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    font-family: "Source Sans Pro Light", sans-serif;
    display: flex;
    align-items: center;
    justify-content: center;

    &__modal {
      background-color: white;
      width: 520px;
      max-height: 80vh;
      padding: 0.5em;
      display: flex;
      flex-direction: column;
      z-index: $modal-z-index;
    }

    &__title {
      font-size: 1.2em;
      padding: 0.5em 0 1em 0;
      width: 100%;
    }

    &__browser {
      height: 40vh;
    }

    &__inputBox {
      display: flex;
      align-items: center;
      padding: 1em 0.5em 0.5em 0.5em;
    }

    &__input {
      flex: 1;
    }

    &__button {
      margin: 0 0.25em;
    }

    &__path {
      margin: 0.25em;
      font-size: 0.7em;
      font-style: italic;
    }
  }
</style>
