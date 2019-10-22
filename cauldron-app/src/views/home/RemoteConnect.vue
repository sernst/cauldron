<template lang="pug">
    .RemoteConnect.tooltip.is-tooltip-right(
      data-tooltip="Manage remote connection"
      :class="{ 'RemoteConnect--connected': connected, 'RemoteConnect--disconnected': !connected }"
    )
      .material-icons {{ icon }}
</template>

<script>
function icon() {
  return this.status.connected ? 'link' : 'link_off';
}

function connected() {
  return this.status.connected || false;
}

export default {
  name: 'RemoteConnect',
  props: {
    status: { type: Object, default: () => {} },
  },
  computed: { connected, icon },
};
</script>

<style scoped lang="scss">
  .RemoteConnect {
    font-size: 0.3em;
    padding: 0.5em 0.5em 0 0.5em;
    border-radius: 5em;
    cursor: pointer;

    &--connected {
      background-color: blue;
      border: 1px solid green;

      &:hover {

      }
    }

    &--disconnected {
      color: #666;
      border: 1px solid #CCC;

      &:hover {
        color: #333;
        background-color: #CCC;
        border: 1px solid #333;
      }
    }
  }
</style>
