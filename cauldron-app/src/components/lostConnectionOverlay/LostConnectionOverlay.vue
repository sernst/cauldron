<template lang="pug">
  .LostConnectionOverlay
    .LostConnectionOverlay__focus
      .LostConnectionOverlay__headerBox
        i.LostConnectionOverlay__icon.material-icons.md-36 signal_wifi_off
        .LostConnectionOverlay__titleBox
          .LostConnectionOverlay__titleHeader No Response
          .LostConnectionOverlay__title Lost Kernel Connection
      .LostConnectionOverlay__infoBox
          .LostConnectionOverlay__message
            | Trying to re-establish communication with the Cauldron kernel...
</template>

<script>
export default {
  name: 'LostConnectionOverlay',
};
</script>

<style scoped lang="scss">
  @import '../../Variables';

  .LostConnectionOverlay {
    font-family: "Source Sans Pro Light", sans-serif;
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: $lost-connect-z-index;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: rgb(215, 215, 215);
    color: #6e6e6e;

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
  }
</style>
