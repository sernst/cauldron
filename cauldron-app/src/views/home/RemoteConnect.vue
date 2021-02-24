<template lang="pug">
    .RemoteConnect.tooltip.is-tooltip-right(
      :data-tooltip="tooltip"
      :class="{ 'RemoteConnect--connected': connected, 'RemoteConnect--disconnected': !connected }"
    )
      .material-icons {{ icon }}
</template>

<script>
function tooltip() {
  const type = this.connected ? 'remote' : 'local';
  const url = this.status?.remote?.url || null;
  const suffix = this.connected ? `at ${url}` : 'alongside the UI.';
  return `Running a ${type} kernel connection ${suffix}`;
}

function icon() {
  return this.connected ? 'link' : 'link_off';
}

function connected() {
  return this.status?.remote?.active || false;
}

export default {
  name: 'RemoteConnect',
  props: {
    status: { type: Object, default: () => {} },
  },
  computed: { connected, icon, tooltip },
};
</script>

<style scoped lang="scss">
  .RemoteConnect {
    font-size: 0.3em;
    padding: 0.5em 0.5em 0 0.5em;
    border-radius: 5em;
    cursor: pointer;

    &--connected {
      color: #51b76a;
      background-color: #ccffd9;
      border: 1px solid #51b76a;
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
