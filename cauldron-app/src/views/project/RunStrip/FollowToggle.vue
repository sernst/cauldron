<template lang="pug">
  .FollowToggle(
    @click="onClick"
    content="Follow Step Changes"
    v-tippy="{ placement: 'right', delay: [200, 0] }"
  )
    i.material-icons.md-18 {{ icon }}
</template>

<script>
/**
 * Property specifying whether or not the follow steps setting is
 * toggled on or off.
 */
function following() {
  return this.$store.getters.followSteps;
}

/**
 * Name of the icon to display within the button, which is
 * different depending on whether or not the follow state
 * is true or false.
 */
function icon() {
  return this.following ? 'visibility' : 'visibility_off';
}

/**
 * Toggles the follow state setting.
 */
function onClick() {
  this.$store.commit('followSteps', !this.following);
}

function data() {
  return {};
}

export default {
  name: 'FollowToggle',
  data,
  computed: { following, icon },
  methods: { onClick },
};
</script>

<style scoped lang="scss">
  .FollowToggle {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0.25em;
    user-select: none;
    cursor: pointer;
    border-top: 1px solid #DEDEDE;

    &:focus {
      outline: none;
    }

    &:hover {
      opacity: 0.7;
    }
  }
</style>
