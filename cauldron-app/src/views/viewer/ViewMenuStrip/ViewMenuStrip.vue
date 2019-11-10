<template lang="pug">
    .ViewMenuStrip
      .ViewMenuStrip__button(@click="onCloseView")
        i.material-icons.md-18 close
</template>

<script>
function onCloseView(event) {
  this.$emit('close', { event });
}

export default {
  name: 'ViewMenuStrip',
  methods: { onCloseView },
};
</script>

<style scoped lang="scss">
  .ViewMenuStrip {
    font-family: "Source Sans Pro", sans-serif;
    color: #333;
    background-color: #CCC;
    height: 100%;
    padding-top: 0.5em;

    &__button {
      padding: 0.5em;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;

      &:hover {
        opacity: 0.7;
      }
    }
  }
</style>
