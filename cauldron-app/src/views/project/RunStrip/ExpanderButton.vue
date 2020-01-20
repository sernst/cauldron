<template lang="pug">
  .ExpanderButton(@click="toggle")
    i.ExpanderButton__icon.material-icons(:class="iconClasses") menu_open
</template>

<script>
function toggle() {
  this.$emit('toggle');
}

function iconClasses() {
  const prefix = 'ExpanderButton__icon';
  return [
    this.state ? `${prefix}--opened` : `${prefix}--closed`,
  ];
}

export default {
  name: 'ExpanderButton',
  props: {
    state: { type: Boolean, required: true },
  },
  computed: { iconClasses },
  methods: { toggle },
};
</script>

<style scoped lang="scss">
  @import "../../../Variables";

  .ExpanderButton {
    width: 3.2em;
    height: 1.5em;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    background-color: #EEE;
    border-top: 1px solid #DEDEDE;
    user-select: none;
    z-index: $over-z-index;

    &__icon {
      font-size: 1.2em;

      &--opened {
        transform: rotate(0deg);
      }

      &--closed {
        transform: rotate(180deg);
      }

      &:hover {
        color: #AAA;
      }
    }
  }
</style>
