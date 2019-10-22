<template lang="pug">
  .AlertDialog
    .AlertDialog__title {{ title }}
    .AlertDialog__message(v-if="message && message.length > 0") {{ message }}
    .AlertDialog__slot
      slot
    .AlertDialog__buttonBox
      .AlertDialog__spacer
      button.AlertDialog__button.button.is-small.is-success(@click="onClick") {{ okLabel }}
</template>

<script>
function data() {
  return {};
}

function onClick() {
  this.$emit('ok');
}

export default {
  name: 'AlertDialog',
  props: {
    title: { type: String, default: 'Alert!' },
    message: { type: String, default: null },
    okLabel: { type: String, default: 'OK' },
  },
  data,
  methods: { onClick },
};
</script>

<style scoped lang="scss">
  @import "../../Variables";

  .AlertDialog {
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

    &__spacer {
      flex: 1;
    }
  }
</style>
