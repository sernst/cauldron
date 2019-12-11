<template lang="pug">
  .ProjectItem(
    v-on:click="openProject"
  )
    .ProjectItem__leftBox
      i.ProjectItem__icon.material-icons.md-18 folder_open
    .ProjectItem__box
      .ProjectItem__title {{ item.name }}
      .ProjectItem__path {{ path }}
      .ProjectItem__date(
        :content="item.modified.display"
        v-tippy="{ placement: 'top' }"
      ) {{ item.modified.elapsed }}
</template>

<script>
function openProject(event) {
  return this.$emit('click', { event, item: this.item });
}

function path() {
  const directory = this.item.directory.absolute;
  return directory.slice(this.root.length);
}

export default {
  name: 'ProjectItem',
  props: {
    item: { type: Object, default: () => {} },
    root: { type: String, default: '' },
  },
  computed: { path },
  methods: { openProject },
};
</script>

<style scoped lang="scss">
  .ProjectItem {
    margin-left: 1em;
    display: flex;
    font-family: "Source Sans Pro", sans-serif;
    padding: 0.25em 0.25em 0.25em 1em;
    cursor: pointer;
    /*border-bottom-left-radius: 1em;*/
    /*border-top-left-radius: 1em;*/
    overflow: visible;
    border-left: 1px dotted #CCCCCC;

    &:hover {
      background-color: #EFEFEF;
    }

    &__leftBox {
      display: flex;
      padding-right: 0.5em;
      /*align-items: center;*/
      justify-content: center;
    }

    &__box {
      flex: 1;
    }

    &__icon {
      color: #666;
    }

    &__title {
      font-size: 1em;
    }

    &__path {
      font-size: 0.6em;
      opacity: 0.8;
    }

    &__date {
      font-size: 0.6em;
      opacity: 0.8;
    }

    &__tipBox {
      display: block;
      text-align: right;
      font-size: 0.8em;
    }
  }
</style>
