<template lang="pug">
  .ProjectFolder(@click="onClick")
    i.ProjectFolder__icon.material-icons.md-14 open_in_browser
    .ProjectFolder__label {{ location.spec.name || location.spec.id }}
</template>

<script>
function data() {
  return {};
}

function onClick(event) {
  this.$emit('select', { event, value: this.location, type: 'project' });
}

export default {
  name: 'ProjectFolder',
  props: {
    location: { type: Object, default: () => {} },
  },
  data,
  methods: { onClick },
};
</script>

<style scoped lang="scss">
  .ProjectFolder {
    display: flex;
    padding: 0.2em;
    align-items: center;
    user-select: none;
    cursor: pointer;
    color: #567c4b;

    &:hover {
      background-color: #accfab;
      color: #47673e;
    }

    &__icon {
      margin-right: 0.5em;
    }

    &__label {
      font-size: 0.7em;
    }
  }
</style>
