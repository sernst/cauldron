<template lang="pug">
  .ErrorOverlay
    .ErrorOverlay__focus
      .ErrorOverlay__headerBox
        i.ErrorOverlay__icon.material-icons.md-36 error_outline
        .ErrorOverlay__titleBox
          .ErrorOverlay__titleHeader Error
          .ErrorOverlay__title {{ error.code }}
      .ErrorOverlay__infoBox
          .ErrorOverlay__message {{ error.message }}
      .ErrorOverlay__buttonBox
        .ErrorOverlay__spacer
        button.ErrorOverlay__button.button.is-small(@click="onDismiss") OK
</template>

<script>
function data() {
  return {};
}

function onDismiss() {
  this.$emit('close');
}

export default {
  name: 'ErrorOverlay',
  props: {
    error: { type: Object, default: () => {} },
  },
  data,
  methods: { onDismiss },
};
</script>

<style scoped lang="scss">
  @import '../../Variables';

  .ErrorOverlay {
    font-family: "Source Sans Pro Light", sans-serif;
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: $error-z-index;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: rgb(128, 75, 72);
    color: white;

    &__headerBox {
      display: flex;
      align-items: center;
      margin-bottom: 0.5em;
      line-height: 1.0em;
    }

    &__titleBox {
      padding-left: 0.5em;
    }

    &__titleHeader {
      font-size: 0.8em;
      opacity: 0.5;
    }

    &__title {
      font-size: 1.2em;
      font-family: monospace;
    }

    &__message {
      max-width: 640px;
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
