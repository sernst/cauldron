<template lang="pug">
  .WarningOverlay
    .WarningOverlay__focus
      .WarningOverlay__headerBox
        i.WarningOverlay__icon.material-icons.md-36 warning
        .WarningOverlay__titleBox
          .WarningOverlay__titleHeader Warning
          .WarningOverlay__title {{ warning.code }}
      .WarningOverlay__infoBox
          .WarningOverlay__message {{ warning.message }}
      .WarningOverlay__buttonBox
        .WarningOverlay__spacer
        button.WarningOverlay__button.button.is-small.is-dark(@click="onDismiss") OK
</template>

<script>
function data() {
  return {};
}

function onDismiss() {
  this.$emit('close');
}

export default {
  name: 'WarningOverlay',
  props: {
    warning: { type: Object, default: () => {} },
  },
  data,
  methods: { onDismiss },
};
</script>

<style scoped lang="scss">
  @import '../../Variables';

  .WarningOverlay {
    font-family: "Source Sans Pro Light", sans-serif;
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: $warning-z-index;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: rgb(199, 170, 106);
    color: #28251c;

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
      opacity: 0.75;
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
