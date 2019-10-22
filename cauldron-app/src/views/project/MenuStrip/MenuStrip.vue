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

function onAction(event) {
  this.$emit(event.action, event);
}

function running() {
  return this.$store.getters.running;
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
