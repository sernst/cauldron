<template lang="pug">
  .Browser

    // The toolbar contains quick-navigation buttons to other locations. The
    // standard locations are shown first, which are locations sent back from
    // the location object (e.g. user's home directory). The extra locations
    // are a property that can be set for custom locations in the UI
    // (e.g. current project directory).
    .Browser__toolbar
      standard-path-button(
        v-for="location in location.standard_locations"
        :value="location"
        @select="onSelect"
      )
      standard-path-button(
        v-for="location in extraLocations"
        :value="location"
        @select="onSelect"
      )

    // Displays the current directory path in which the contents below reside.
    .Browser__path {{ location.current_directory }}

    .Browser__box(ref="scroller")
      // Folder display
      .Browser__folders(v-if="showFolders")
        folder(v-if="location.parent_directory" :value="parentFolder" @select="onSelect")
        folder(v-for="child in foldersToShow" :value="child" @select="onSelect")
        // Project display
        project-folder(
          v-if="projectSelection && location.spec"
          :location="location"
          @select="onSelect"
        )

      // File display
      .Browser__files(v-if="showFiles")
        file(v-for="child in filesToShow" :value="child" @select="onSelect")
      .Browser__padding
</template>

<script>
import Folder from './Folder.vue';
import ProjectFolder from './ProjectFolder.vue';
import File from './File.vue';
import StandardPathButton from './StandardPathButton.vue';

/**
 * Returns the list of folder objects from the location property to show in the
 * browser. If folders are not set to be shown, an empty list will always be
 * returned instead.
 */
function foldersToShow() {
  if (!this.showFolders) {
    return [];
  }

  return (this.location || {}).children || [];
}

/**
 * Returns the list of file objects from the location property to show in the
 * browser. If files are not set to be shown, an empty list will always be
 * returned instead. If extensions have been set on the browser, only files
 * ending with those extensions will be shown in the display.
 */
function filesToShow() {
  if (!this.showFiles) {
    return [];
  }

  const files = (this.location || {}).current_files || [];
  if (!this.extensions || this.extensions.length === 0) {
    return files;
  }

  // For each file, check to see if it matches at least one of the specified extensions.
  return files.filter(f => this.extensions.filter(e => f.name.endsWith(e)).length > 0);
}

/**
 * When a file or folder is selected, this fires to inform the containing component
 * of the selection. The event object is a file or folder event created in the
 * children components and is passed up to the parent through this event.
 */
function onSelect(event) {
  this.$emit('select', event);
}

/**
 * Returns the specification for the parent directory of the current location
 * by assembling a location object based on the parent_directory of the
 * current location.
 */
function parentFolder() {
  return {
    folder: '..',
    directory: this.location.parent_directory,
    spec: null,
    parent: null,
  };
}

/**
 * When the location value changes, the browser box should be scrolled
 * back to the top.
 */
function watchLocation() {
  this.$refs.scroller.scrollTop = 0;
}

export default {
  name: 'Browser',
  components: {
    StandardPathButton,
    Folder,
    ProjectFolder,
    File,
  },
  props: {
    location: { type: Object, default: () => {} },
    showFiles: { type: Boolean, default: true },
    showFolders: { type: Boolean, default: true },
    extraLocations: { type: Array, default: () => [] },
    extensions: { type: Array, default: () => [] },
    projectSelection: { type: Boolean, default: false },
  },
  computed: { parentFolder, foldersToShow, filesToShow },
  watch: {
    location: watchLocation,
  },
  methods: { onSelect },
};
</script>

<style scoped lang="scss">
  .Browser {
    font-family: "Source Sans Pro", sans-serif;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    height: 100%;

    &__toolbar {
      display: flex;
      margin-bottom: 0.25em;
      justify-content: flex-end;
    }

    &__path {
      color: #444;
      font-size: 0.6em;
      padding: 0.2em;
      background-color: #EEE;
    }

    &__box {
      overflow-y: scroll;
      flex: 1;
      border: 1px solid #EEE;
    }

    &__padding {
      height: 100px;
    }
  }
</style>
