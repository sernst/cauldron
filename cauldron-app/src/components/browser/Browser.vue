<template lang="pug">
  .Browser
    .Browser__toolbar
      standard-path-button(
        v-for="location in location.standard_locations"
        :value="location"
        @select="onSelect"
      )
    .Browser__path {{ location.current_directory }}
    .Browser__box
      folder(v-if="location.parent_directory" :value="parentFolder" @select="onSelect")
      folder(v-for="child in location.children" :value="child" @select="onSelect")
      .Browser__files(v-if="showFiles")
        file(v-for="child in location.current_files" :value="child" @select="onSelect")
      .Browser__padding

</template>

<script>
import Folder from './Folder.vue';
import File from './File.vue';
import StandardPathButton from './StandardPathButton.vue';

function data() {
  return {};
}

function onSelect(event) {
  this.$emit('select', event);
}

function parentFolder() {
  return {
    folder: '..',
    directory: this.location.parent_directory,
    spec: null,
    parent: null,
  };
}

export default {
  name: 'Browser',
  components: { StandardPathButton, Folder, File },
  props: {
    location: { type: Object, default: () => {} },
    showFiles: { type: Boolean, default: true },
  },
  data,
  computed: { parentFolder },
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
