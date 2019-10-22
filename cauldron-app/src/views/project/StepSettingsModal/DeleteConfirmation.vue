<template lang="pug">
  .DeleteConfirmation
    .DeleteConfirmation__title Confirm Step Removal
    .DeleteConfirmation__messageBox
      | Are you sure you want to remove the "{{ step.name }}" step from this project?
      | This action cannot be undone.
    .DeleteConfirmation__inputBox
      label.checkbox.is-small
        input(type="checkbox" v-model="removeDeletedFile")
        span Delete source file as well
    .DeleteConfirmation__buttonBox
      .DeleteConfirmation__spacer
      .DeleteConfirmation__button.button.is-small(
        @click.stop="onConfirm(false, $event)"
      ) Cancel
      .DeleteConfirmation__button.button.is-small.is-danger(
        @click.stop="onConfirm(true, $event)"
      ) Delete
</template>

<script>
function data() {
  return {
    removeDeletedFile: true,
  };
}

function onConfirm(confirmed, event) {
  this.$emit('confirmed', { confirmed, event, removeDeletedFile: this.removeDeletedFile });
}

export default {
  name: 'DeleteConfirmation',
  props: {
    step: { type: Object, default: () => {} },
  },
  data,
  methods: { onConfirm },
};
</script>

<style scoped lang="scss">
  @import '../../../Variables';

  .DeleteConfirmation {
    background-color: white;
    max-width: 480px;
    min-width: 320px;
    padding: 0.5em;
    z-index: $modal-z-index;

    &__title {
      font-size: 1.2em;
      margin-top: 0.5em;
      margin-bottom: 0.5em;
      text-align: center;
      width: 100%;
    }

    &__messageBox {
      margin: 0.5em;
      font-size: 0.9em;
    }

    &__inputBox {
      padding: 0.5em;
    }

    &__buttonBox {
      display: flex;
      margin-top: 1em;
    }

    &__button {
      margin: 0 0.25em;
    }

    &__spacer {
      flex: 1;
    }
  }
</style>
