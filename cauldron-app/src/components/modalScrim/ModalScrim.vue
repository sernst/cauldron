<template lang="pug">
  .ModalScrim(@click="onClick")
    .ModalScrim__loadingBox(v-if="message")
      spinner(theme="dark")
      .ModalScrim__loadingMessage {{ message }}
</template>

<script>
import Spinner from '../spinner/Spinner.vue';

function onClick(event) {
  this.$emit('click', event);
}

function data() {
  return {};
}

export default {
  name: 'ModalScrim',
  components: { Spinner },
  props: {
    message: { type: String, default: null },
  },
  data,
  methods: { onClick },
};
</script>

<style scoped lang="scss">
  @import '../../Variables';

  .ModalScrim {
    font-family: "Source Sans Pro Light", sans-serif;
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: $modal-scrim-z-index;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: rgba(0, 0, 0, 0.75);
    color: white;
  }
</style>
