<template lang="pug">
    .MenuStripItem(
      @mouseover="onToggleShow(true, $event)"
      @mouseleave="onToggleShow(false, $event)"
    )
      .MenuStripItem__box
        i.material-icons.md-18 {{ icon }}
      .MenuStripItem__overlay(v-if="show")
        .MenuStripItem__titleBox
          .MenuStripItem__title {{ title }}
        .MenuStripItem__customBox
          slot
</template>

<script>
function data() {
  return {
    show: false,
    delayTimeout: null,
  };
}

function onToggleShow(state) {
  clearTimeout(this.delayTimeout);
  this.delayTimeout = setTimeout(() => {
    this.show = state;
  }, 150);
}

export default {
  name: 'MenuStripItem',
  props: {
    icon: { type: String, default: 'home' },
    title: { type: String, default: 'Menu' },
  },
  data,
  methods: { onToggleShow },
};
</script>

<style scoped lang="scss">
  @import '../../../Variables';

  .MenuStripItem {
    position: relative;

    &__box {
      color: #333;
      display: flex;
      align-items: center;
      justify-content: center;
      padding-bottom: 1em;
      cursor: pointer;

      &:hover {
        opacity: 0.7;
      }
    }

    &__titleBox {
      font-size: 0.7em;
      font-weight: bolder;
      background-color: #DDD;
      padding: 0.25em 0 0.25em 1em;
    }

    &__overlay {
      position: absolute;
      top: -0.5em;
      left: 2em;
      z-index: $menu-z-index;
      min-width: 200px;
      background-color: #EEE;
      border: 1px solid #DDD;
    }
  }
</style>
