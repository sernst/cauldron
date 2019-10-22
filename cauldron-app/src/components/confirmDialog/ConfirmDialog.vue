<template lang="pug">
  .ConfirmDialog
    .ConfirmDialog__title {{ title }}
    .ConfirmDialog__message(v-if="message && message.length > 0") {{ message }}
    .ConfirmDialog__slot
      slot
    .ConfirmDialog__buttonBox
      .ConfirmDialog__spacer
      button.ConfirmDialog__button.button.is-small(@click="onNo") {{ noLabel }}
      button.ConfirmDialog__button.button.is-small(@click="onYes") {{ yesLabel }}
</template>

<script>
function data() {
  return {};
}

function onYes() {
  this.$emit('yes');
}

function onNo() {
  this.$emit('no');
}

export default {
  name: 'ConfirmDialog',
  props: {
    title: { type: String, default: 'Confirm' },
    message: { type: String, default: null },
    yesLabel: { type: String, default: 'OK' },
    noLabel: { type: String, default: 'Cancel' },
  },
  data,
  methods: { onYes, onNo },
};
</script>

<style scoped lang="scss">
  @import "../../Variables";

  .ConfirmDialog {
    background-color: white;
    z-index: $modal-z-index;
    padding: 0.5em;

    &__title {
      font-size: 1.2em;
      padding: 0.5em;
      width: 100%;
    }

    &__message {
      font-size: 0.8em;
      color: #444;
    }

    &__buttonBox {
      margin-top: 0.75em;
      display: flex;
    }

    &__button {
      margin: 0 0.25em;
    }

    &__spacer {
      flex: 1;
    }
  }
</style>
