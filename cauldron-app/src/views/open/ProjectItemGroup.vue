<template lang="pug">
  .ProjectItemGroup
    .ProjectItemGroup__header(@click.stop="onClick")
      i.ProjectItemGroup__icon.material-icons.md-14 {{ groupIcon }}
      .ProjectItemGroup__label {{ root }}
    .ProjectItemGroup__children(v-if="!collapsed")
      project-item(
        v-for="item in items"
        :item="item"
        :root="root"
        @click="onProjectClick"
      )
</template>

<script>
import ProjectItem from './ProjectItem.vue';

function onClick() {
  const current = this.collapsed;
  this.collapsed = !current;
  this.$emit('collapse', { root: this.root, collapsed: this.collapsed });
}

function onProjectClick(event) {
  this.$emit('open', event);
}

function groupIcon() {
  return this.collapsed ? 'keyboard_arrow_up' : 'keyboard_arrow_down';
}

function data() {
  return {
    collapsed: false,
  };
}

export default {
  name: 'ProjectItemGroup',
  components: { ProjectItem },
  props: {
    root: { type: String, default: '' },
    items: { type: Array, default: () => [] },
  },
  data,
  computed: { groupIcon },
  methods: { onClick, onProjectClick },
};
</script>

<style scoped lang="scss">
  .ProjectItemGroup {
    &__header {
      padding: 1em;
      font-size: 0.7em;
      display: flex;
      align-items: center;
      user-select: none;
      cursor: pointer;

      &:hover {
        opacity: 0.7;
      }
    }

    &__icon {
      margin-right: 1em;
    }
  }
</style>
