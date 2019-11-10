<template lang="pug">
    .MenuStripItem(
      @click="onToggleShow(null, 0)"
      @mouseover="onMouseOver"
      @mouseleave="onToggleShow(false, 300)"
    )
      .MenuStripItem__box(:class="boxClasses")
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

function boxClasses() {
  const blockElement = 'MenuStripItem__box';
  const modifier = this.show ? 'opened' : 'closed';
  return `${blockElement}--${modifier}`;
}

function onMouseOver() {
  if (this.show) {
    // If the menu is currently showing, a mouse over should keep it showing.
    // This deals with the situation where a user briefly mouses out but comes
    // back before the timeout to hide the overlay is reached.
    clearTimeout(this.delayTimeout);
  }
}

function onToggleShow(state, delay) {
  const newState = state === null ? !this.show : state;
  clearTimeout(this.delayTimeout);
  this.delayTimeout = setTimeout(() => {
    this.show = newState;
  }, delay);
}

export default {
  name: 'MenuStripItem',
  props: {
    icon: { type: String, default: 'home' },
    title: { type: String, default: 'Menu' },
  },
  data,
  computed: { boxClasses },
  methods: { onToggleShow, onMouseOver },
};
</script>

<style scoped lang="scss">
  @import '../../../Variables';

  .MenuStripItem {
    position: relative;

    &__box {
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0.75em 0;
      cursor: pointer;

      &--closed {
        color: #333;

        &:hover {
          opacity: 0.7;
          background-color: rgba(0, 0, 0, 0.1);
        }
      }

      &--opened {
        color: #EEE;
        background-color: #444;

        &:hover {
          opacity: 0.7;
          background-color: #777;
        }
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
