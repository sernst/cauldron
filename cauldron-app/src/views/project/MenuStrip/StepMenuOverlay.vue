<template lang="pug">
  .StepMenuOverlay
    menu-button(
      icon="playlist_add"
      :flipped="true"
      label="Insert Before"
      @click="insertStep('before')"
    )
    menu-button(icon="playlist_add" label="Insert After" @click="insertStep('after')")
    .StepMenuOverlay__separator
    menu-button(icon="sentiment_satisfied" label="Clear Unhappy Faces" @click="cleanStepStatuses")
</template>

<script>
import http from '../../../http';
import MenuButton from './MenuButton.vue';
import notebook from '../../../notebook';
import loading from '../../../loading';

function data() {
  return {};
}

function cleanStepStatuses() {
  this.$parent.show = false;
  return http.execute('steps clean')
    .then((response) => {
      if (!response.data.success) {
        return response;
      }
      this.$store.commit('project', response.data.data.project);
      return response;
    });
}

/**
 * Inserts a new step with automatic naming and settings either `before` or `after`
 * the currently selected step depending upon the enumerated value of the location
 * property.
 */
function insertStep(location) {
  loading.show('INSERT_STEP', 'Adding new step');
  this.$parent.show = false;
  const { steps } = this.$store.getters.project;
  const selectedIndex = steps.reduce((result, step, index) => {
    const { selected } = step.status;
    return selected ? index : result;
  }, 0);
  const offset = location === 'before' ? -1 : 0;
  const beforeIndex = selectedIndex + offset;
  const position = beforeIndex >= 0 ? steps[beforeIndex].name : '0';

  return http
    .execute(`steps add --position="${position}"`)
    .then((response) => {
      const payload = response.data;
      return notebook.applyStepModifications(
        payload.data.step_renames,
        payload.data.step_changes,
      );
    })
    .then(() => {
      http.markStatusDirty();
      loading.hide('INSERT_STEP');
    });
}

export default {
  name: 'StepMenuOverlay',
  components: { MenuButton },
  data,
  methods: { insertStep, cleanStepStatuses },
};
</script>

<style scoped lang="scss">
  .StepMenuOverlay {
    &__separator {
      height: 1px;
      width: 100%;
      margin: 0.1em 0;
      background-color: rgba(0, 0, 0, 0.1);
    }
  }
</style>
