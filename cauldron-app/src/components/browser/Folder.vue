<template lang="pug">
  .Folder(@click="onClick")
    i.Folder__icon.material-icons.md-14 {{ icon }}
    .Folder__label {{ value.folder }}
</template>

<script>
function data() {
  return {};
}

function icon() {
  return this.value.spec ? 'folder_open' : 'folder';
}

function onClick(event) {
  this.$emit('select', { event, value: this.value, type: 'folder' });
}

export default {
  name: 'Folder',
  props: {
    value: { type: Object, default: () => {} },
  },
  data,
  computed: { icon },
  methods: { onClick },
};
</script>

<style scoped lang="scss">
  .Folder {
    color: #444;
    display: flex;
    padding: 0.2em;
    align-items: center;
    user-select: none;
    cursor: pointer;

    &:hover {
      background-color: #EFEFEF;
      color: black;
    }

    &__icon {
      margin-right: 0.5em;
    }

    &__label {
      font-size: 0.7em;
    }
  }
</style>
