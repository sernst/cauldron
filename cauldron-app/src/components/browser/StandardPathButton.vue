<template lang="pug">
  .StandardPathButton(
    :content="value.label"
    v-tippy="{ placement: 'top' }"
    @click="onClick"
  )
    i.StandardPathButton__icon.material-icons.md-14(v-if="icon") {{ icon }}
    .StandardPathButton__label(v-if="!icon") {{ firstCharacter }}
</template>

<script>
function icon() {
  const label = (this.value.label || '').toLocaleLowerCase();
  if (label.includes('home')) {
    return 'home';
  }
  if (label.includes('parent')) {
    return 'arrow_upward';
  }
  if (label.includes('project')) {
    return 'folder_open';
  }
  return null;
}

function firstCharacter() {
  return (this.value.label || '?').substr(0, 1);
}

function onClick(event) {
  this.$emit('select', { event, value: this.value });
}

function data() {
  return {};
}

export default {
  name: 'StandardPathButton',
  props: {
    value: { type: Object, default: () => {} },
  },
  data,
  computed: { icon, firstCharacter },
  methods: { onClick },
};
</script>

<style scoped lang="scss">
  .StandardPathButton {
    width: 1.4em;
    height: 1.4em;
    border-radius: 2em;
    background-color: white;
    margin-left: 0.25em;
    color: #999;
    border: 1px solid #999;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    cursor: pointer;
    user-select: none;

    &:hover {
      background-color: #EFEFEF;
      color: #444;
      border: 1px solid #444;
    }
  }
</style>
