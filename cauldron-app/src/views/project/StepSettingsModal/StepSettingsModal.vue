<template lang="pug">
  .StepSettingsModal
    modal-scrim(:message="loadingMessage" @click="onCancel")

    .StepSettingsModal__modal(v-if="!confirmingDelete && !loadingMessage")
      .StepSettingsModal__title Modify Step "{{ step.name }}"
      .StepSettingsModal__inputBox
        .StepSettingsModal__header Step Name
        input.input.is-small(type="text" placeholder="Step Name..." v-model="stepSuffix")
      .StepSettingsModal__inputBox
        .StepSettingsModal__header File Type
        .select.is-small
          select(v-model="extension")
            option(
              v-for="type in fileTypes"
              :value="type.extension"
            ) {{ type.label }}
      .StepSettingsModal__inputBox
        .StepSettingsModal__header Located After
        .select.is-small
          select(v-model="location")
            option(
              v-for="location in locations"
              :value="location.id"
            ) {{ location.label }}
      .StepSettingsModal__buttonBox
        .StepSettingsModal__button.button.is-small.is-danger(
          @click="onDelete"
          v-if="allowDelete"
        ) Remove
        .StepSettingsModal__spacer
        .StepSettingsModal__button.button.is-small(@click="onCancel") Cancel
        .StepSettingsModal__button.button.is-small.is-success(@click="onApply") Apply

    delete-confirmation(
      v-if="confirmingDelete && !loadingMessage"
      :step="step"
      @confirmed="onDeleteConfirmed"
    )
</template>

<script>
import ModalScrim from '../../../components/modalScrim/ModalScrim.vue';
import http from '../../../http';
import notebook from '../../../notebook';
import DeleteConfirmation from './DeleteConfirmation.vue';

function allowDelete() {
  return ((this.$store.getters.project || {}).steps || []).length > 1;
}

function onDelete() {
  this.confirmingDelete = true;
}

function onDeleteConfirmed(event) {
  this.confirmingDelete = false;

  if (!event.confirmed) {
    return Promise.resolve();
  }

  this.loadingMessage = `Removing "${this.step.name}" step`;
  const command = [
    'steps remove',
    `"${this.step.name}"`,
    event.removeDeletedFile ? '' : ' --keep',
  ];

  return http.execute(command.filter((line) => line.length > 0).join(' '))
    .then((response) => {
      if (!response.data.success) {
        return Promise.resolve();
      }

      const payload = response.data;
      return notebook.applyStepModifications(
        payload.data.step_renames,
        payload.data.step_changes,
      );
    })
    .finally(() => {
      this.$emit('close', { action: 'deleted' });
    });
}

function onCancel() {
  this.$emit('close', {});
}

function stepName() {
  const { prefix } = this.initialValues;
  const separator = this.stepSuffix.length > 0 ? '-' : '';
  return `${prefix}${separator}${this.stepSuffix}.${this.extension}`;
}

function onApply() {
  const changes = [
    { key: 'newName', after: this.stepName, before: this.step.name },
    { key: 'newTitle', after: this.title, before: this.initialValues.title },
    { key: 'newLocation', after: this.location, before: this.initialValues.location },
  ]
    .filter((e) => e.after !== e.before)
    .reduce((combined, e) => Object.assign(combined, { [e.key]: e.after }), {});

  const hasModifications = Object.keys(changes).length > 0;
  if (!hasModifications) {
    this.$emit('close', {});
    return Promise.resolve();
  }

  this.loadingMessage = `Updating step "${changes.newName || this.step.name}"`;
  const command = [
    'steps modify',
    `"${this.step.name}"`,
    changes.newName ? `--name="${changes.newName}"` : '',
    changes.newTitle ? `--title="${changes.newTitle}"` : '',
    changes.newLocation ? `--position="${changes.newLocation}"` : '',
  ];

  return http.execute(command.filter((line) => line.length > 0).join(' '))
    .then((response) => {
      if (!response.data.success) {
        return Promise.resolve();
      }

      const payload = response.data;
      return notebook.applyStepModifications(
        payload.data.step_renames,
        payload.data.step_changes,
      );
    })
    .finally(() => {
      this.loadingMessage = null;
      this.$emit('close', {});
    });
}

function data() {
  return {
    initialValues: {},
    stepSuffix: null,
    title: null,
    extension: null,
    location: '0',
    fileTypes: [
      { label: 'Python (*.py)', extension: 'py' },
      { label: 'Markdown (*.md)', extension: 'md' },
      { label: 'HTML (*.html)', extension: 'html' },
      { label: 'JavaScript (*.js)', extension: 'js' },
      { label: 'JSON (*.json)', extension: 'json' },
    ],
    locations: [],
    confirmingDelete: false,
    loadingMessage: null,
  };
}

function mounted() {
  const { step } = this;
  const steps = (this.$store.getters.project || {}).steps || [];
  const explodedName = (step || {}).exploded_name || {};
  const location = step.index === 0 ? '0' : steps[step.index - 1].name;
  const prefix = step.name
    // Remove the suffix and extension from the name.
    .replace(`${explodedName.name}.${explodedName.extension}`, '')
    // Remove trailing `-` if it exists.
    .replace(/-$/, '');

  const initialValues = {
    location,
    prefix,
    suffix: explodedName.name,
    title: step.title,
    extension: explodedName.extension,
  };

  this.initialValues = initialValues;
  this.title = initialValues.title;
  this.stepSuffix = initialValues.suffix;
  this.extension = initialValues.extension;
  this.location = initialValues.location;

  const locations = ((this.$store.getters.project || {}).steps || [])
    .map((s) => ({ label: s.name, id: s.name }))
    .filter((s) => s.label !== step.name);
  locations.unshift({ label: 'Beginning (First step)', id: '0' });
  this.locations = locations;
}

export default {
  name: 'StepSettingsModal',
  components: { DeleteConfirmation, ModalScrim },
  props: {
    step: { type: Object, default: () => {} },
  },
  data,
  computed: { allowDelete, stepName },
  mounted,
  methods: {
    onCancel,
    onApply,
    onDelete,
    onDeleteConfirmed,
  },
};
</script>

<style scoped lang="scss">
  @import '../../../Variables';

  .StepSettingsModal {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    font-family: "Source Sans Pro Light", sans-serif;
    display: flex;
    align-items: center;
    justify-content: center;

    &__modal {
      background-color: white;
      max-width: 480px;
      min-width: 320px;
      padding: 0.5em;
      z-index: $modal-z-index;
    }

    &__title {
      font-size: 1.2em;
      margin-top: 0.5em;
      margin-bottom: 0.5em;
      text-align: center;
      width: 100%;
    }

    &__inputBox {
      padding: 0.5em;
    }

    &__header {
      font-size: 0.8em;
      opacity: 0.8;
      margin-bottom: 0.2em;
    }

    &__buttonBox {
      display: flex;
      margin-top: 1em;
    }

    &__button {
      margin: 0 0.25em;
    }

    &__spacer {
      flex: 1;
    }
  }
</style>
