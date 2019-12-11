<template lang="pug">
  .RecentItem(
    v-on:click="openProject"
  )
    .RecentItem__leftBox
      .material-icons.RecentItem__icon folder_open
    .RecentItem__box
      .RecentItem__title {{ item.name }}
      .RecentItem__path {{ item.directory.short }}
      .RecentItem__date(
        :content="item.modified.display"
        v-tippy="{ placement: 'top' }"
      ) {{ item.modified.elapsed }}
    .RecentItem__rightBox
      .RecentItem__remove.tooltip.is-tooltip-left.is-tooltip-danger(
        data-tooltip="Remove from recent list"
        v-on:click.stop="removeFromRecent"
      )
        i.material-icons.md-18 close
</template>

<script>
function removeFromRecent(event) {
  return this.$emit('click', { action: 'remove', event, item: this.item });
}

function openProject(event) {
  return this.$emit('click', { action: 'open', event, item: this.item });
}

export default {
  name: 'RecentItem',
  props: {
    item: { type: Object, default: () => {} },
  },
  methods: { openProject, removeFromRecent },
};
</script>

<style scoped lang="scss">
  .RecentItem {
    display: flex;
    font-family: "Source Sans Pro", sans-serif;
    padding: 0.5em 0.5em;
    cursor: pointer;
    border-bottom-left-radius: 1em;
    border-top-left-radius: 1em;
    overflow: visible;
    user-select: none;

    &:hover {
      background-color: #EFEFEF;
    }

    &__leftBox {
      display: flex;
      padding-right: 0.5em;
      align-items: center;
      justify-content: center;
    }

    &__rightBox {
      display: flex;
      padding-left: 0.5em;
      align-items: center;
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

    &__remove {
      color: #666;

      &:hover {
        color: hsl(348, 100%, 61%);
      }
    }

    &__tipBox {
      display: block;
      text-align: right;
      font-size: 0.8em;
    }
  }
</style>
