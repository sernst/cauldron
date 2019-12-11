<template lang="pug">
  .MenuButton(@click="onClick")
    i.material-icons.md-18.MenuButton__icon(
      :class="{ 'MenuButton__icon--flipped': flipped }"
    ) {{ icon }}
    .MenuButton__label {{ label }}
</template>

<script>
function onClick(event) {
  this.$emit('click', event);
}

function data() {
  return {};
}

export default {
  name: 'MenuButton',
  props: {
    icon: { type: String, default: 'question' },
    label: { type: String, default: 'Menu Button' },
    flipped: { type: Boolean, default: false },
  },
  data,
  methods: { onClick },
};
</script>

<style scoped lang="scss">
  .MenuButton {
    padding: 0.5em;
    display: flex;
    align-items: center;
    cursor: pointer;
    user-select: none;

    &:hover {
      opacity: 0.7;
      background-color: #EEE;
    }

    &__icon {
      margin-right: 0.25em;

      &--flipped {
        transform: rotate(180deg);
      }
    }

    &__label {
      font-size: 0.8em;
    }
  }
</style>
