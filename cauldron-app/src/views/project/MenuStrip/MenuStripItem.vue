<template lang="pug">
    .MenuStripItem(
      @mouseover="onMouseOver"
      @mouseleave="onToggleShow(false, 300)"
    )
      .MenuStripItem__box(
        @click="onToggleShow(null, 0)"
        :class="boxClasses"
      )
        i.material-icons.md-18 {{ icon }}
      .MenuStripItem__overlay(v-if="show")
        .MenuStripItem__titleBox
          .MenuStripItem__title {{ title }}
        .MenuStripItem__customBox
          project-menu-overlay(
            v-if="shouldShowOverlay('Project')"
            @hide="onHideOverlay"
            @action="onAction"
          )
          step-menu-overlay(
            v-if="shouldShowOverlay('Steps')"
            @hide="onHideOverlay"
            @action="onAction"
          )
          settings-menu-overlay(
            v-if="shouldShowOverlay('Settings')"
            @hide="onHideOverlay"
            @action="onAction"
          )
</template>

<script>
import ProjectMenuOverlay from './ProjectMenuOverlay.vue';
import StepMenuOverlay from './StepMenuOverlay.vue';
import SettingsMenuOverlay from './SettingsMenuOverlay.vue';

function data() {
  return {
    show: false,
    delayTimeout: null,
  };
}

function shouldShowOverlay(identifier) {
  return this.show && identifier === this.title;
}

function onHideOverlay() {
  this.show = false;
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

/**
 * Bubbles events from children up to the parent Project view for event handling.
 */
function onAction(event) {
  this.$emit('action', event);
}

export default {
  name: 'MenuStripItem',
  components: { SettingsMenuOverlay, StepMenuOverlay, ProjectMenuOverlay },
  props: {
    icon: { type: String, default: 'home' },
    title: { type: String, default: 'Menu' },
  },
  data,
  computed: { boxClasses },
  methods: {
    onToggleShow,
    onMouseOver,
    onAction,
    onHideOverlay,
    shouldShowOverlay,
  },
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
      background-color: #FAFAFA;
      border: 1px solid #DDD;
    }
  }
</style>
