<template lang="pug">
  .Loader
    .Loader__focus
      spinner.Loader__spinner
      .Loader__message(v-if="message") {{ message }}
</template>

<script>
import Spinner from '../spinner/Spinner.vue';

function data() {
  return {};
}

export default {
  name: 'Loader',
  components: { Spinner },
  props: {
    message: { type: String, default: '' },
  },
  data,
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
  @import '../../Variables';

  .Loader {
    font-family: "Source Sans Pro Light", sans-serif;
    display: flex;
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: $loader-z-index;
    align-items: center;
    justify-content: center;
    background-color: #FFF;

    &__message {
      padding-top: 0.5em;
      color: #999;
      max-width: 480px;
    }
  }
</style>
