<template lang="pug">
  .File(@click.stop="onClick")
    i.File__icon.material-icons.md-14 {{ icon }}
    .File__label {{ value.name }}
</template>

<script>
function data() {
  return {};
}

function icon() {
  const extension = ((this.file || {}).name || '').split('.').slice(-1)[0].toLocaleLowerCase();
  return extension === 'cauldron' ? 'chrome_reader_mode' : 'insert_drive_file';
}

function onClick(event) {
  const extension = ((this.file || {}).name || '').split('.').slice(-1)[0].toLocaleLowerCase();
  this.$emit('select', {
    event,
    value: this.value,
    type: 'file',
    isReaderFile: extension === 'cauldron',
  });
}

export default {
  name: 'File',
  props: {
    value: { type: Object, default: () => {} },
  },
  data,
  computed: { icon },
  methods: { onClick },
};
</script>

<style scoped lang="scss">
  .File {
    color: #777;
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
