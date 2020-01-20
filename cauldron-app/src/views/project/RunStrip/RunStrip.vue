<template lang="pug">
    .RunStrip
      .RunStripStep__topBox
        .RunStrip__scroller(
          @click="scroll('up')"
          :class="getScrollerClasses('up')"
        )
          i.RunStrip__scrollerIcon.material-icons.md-24 arrow_drop_up
      run-strip-step(
        v-for="(step, index) in steps"
        v-if="index >= visibleIndex"
        :step="step"
        :index="index"
        @aborting="onAborting"
        @aborted="onAborted"
        @settings="onEditSettings"
      )
      .RunStrip__bottomBox
        expander-button(@toggle="toggleExpanderOvleray" :state="showExpanderOverlay")
        follow-toggle
        .RunStrip__scroller(
          @click="scroll('down')"
          :class="getScrollerClasses('down')"
        )
          i.RunStrip__scrollerIcon.material-icons.md-24 arrow_drop_down
</template>

<script>
import RunStripStep from './RunStripStep.vue';
import FollowToggle from './FollowToggle.vue';
import ExpanderButton from './ExpanderButton.vue';

function scroll(direction) {
  const stepCount = (this.steps || []).length;
  const interval = Math.min(5, Math.ceil(stepCount / 5));
  const delta = direction === 'down' ? interval : -1 * interval;
  this.visibleIndex = Math.max(0, Math.min(stepCount - 5, this.visibleIndex + delta));
}

function getScrollerClasses(direction) {
  const index = this.visibleIndex;
  const className = ['RunStrip', '__scroller', '--'];

  if (direction === 'up') {
    className.push(index > 0 ? 'enabled' : 'disabled');
  } else {
    const maxScroll = Math.max(0, (this.steps || []).length - 5);
    className.push(index < maxScroll ? 'enabled' : 'disabled');
  }

  return className.join('');
}

function steps() {
  return (this.$store.getters.project || {}).steps || [];
}

function onAborting(event) {
  this.$emit('aborting', event);
}

function onAborted(event) {
  this.$emit('aborted', event);
}

function onEditSettings(event) {
  this.$emit('settings', event);
}

function toggleExpanderOvleray() {
  this.showExpanderOverlay = !this.showExpanderOverlay
}

function data() {
  return {
    visibleIndex: 0,
    showExpanderOverlay: false,
  };
}

export default {
  name: 'RunStrip',
  components: { ExpanderButton, FollowToggle, RunStripStep },
  data,
  computed: { steps },
  methods: {
    onAborted,
    onAborting,
    onEditSettings,
    scroll,
    getScrollerClasses,
    toggleExpanderOvleray,
  },
};
</script>

<style scoped lang="scss">
  @import "../../../Variables";

  .RunStrip {
    font-family: "Source Sans Pro", sans-serif;
    background-color: #EEE;
    width: 3.2em;
    height: 100%;
    position: relative;

    &__scroller {
      width: 3.2em;
      height: 1.5em;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      background-color: #EEE;
      border-top: 1px solid #DEDEDE;
      border-bottom: 1px solid #DEDEDE;
      user-select: none;
      z-index: $over-z-index;

      &--enabled {
        color: #666;

        &:hover {
          color: #AAA;
        }
      }

      &--disabled {
        color: #CCC;
      }
    }

    &__topBox {
      background-color: #EEE;
      width: 3.2em;
      z-index: $over-z-index;
    }

    &__bottomBox {
      background-color: #EEE;
      width: 3.2em;
      z-index: $over-z-index;
      position: absolute;
      bottom: 0;
      left: 0;
    }
  }
</style>
