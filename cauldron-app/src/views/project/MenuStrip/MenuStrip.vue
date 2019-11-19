<template lang="pug">
    .MenuStrip(
      :class="{'MenuStrip--locked': running}"
    )
      menu-strip-item(icon="folder_open" title="Project")
        project-menu-overlay(@action="onAction")
      menu-strip-item(icon="dns" title="Steps")
        step-menu-overlay(@action="onAction")
</template>

<script>
import ProjectMenuOverlay from './ProjectMenuOverlay.vue';
import StepMenuOverlay from './StepMenuOverlay.vue';
import MenuStripItem from './MenuStripItem.vue';

/**
 * Bubbles events from children up to the parent Project view for event handling.
 */
function onAction(event) {
  this.$emit(event.action, event);
}

/**
 * Whether or not the application is in a running state, which is determined either
 * by a queued step or the running state being true. This is used to disable the
 * project menu to prevent collisions with the running state.
 *
 * @returns {boolean}
 */
function running() {
  const queuedStepsToRun = this.$store.getters.queuedStepsToRun || [];
  return (this.$store.getters.running || queuedStepsToRun.length > 0);
}

export default {
  name: 'MenuStrip',
  components: { MenuStripItem, StepMenuOverlay, ProjectMenuOverlay },
  computed: { running },
  methods: { onAction },
};
</script>

<style scoped lang="scss">
  .MenuStrip {
    font-family: "Source Sans Pro", sans-serif;
    background-color: #EEE;
    width: 2em;
    height: 100%;
    padding-top: 0.5em;

    &--locked {
      pointer-events: none;
      opacity: 0.5;
    }
  }
</style>
