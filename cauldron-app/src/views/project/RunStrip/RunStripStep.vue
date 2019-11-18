<template lang="pug">
    .RunStripStep(
      @mouseover="onToggleShow(true, $event)"
      @mouseleave="onToggleShow(false, $event)"
      :class="getStateClassesFor('')"
    )
      .RunStripStep__box(
        @click.left.exact="focusOnStep"
        @click.left.shift.exact="queueStepToRun"
        @dblclick="queueStepToRun"
      )
        i.material-icons.md-14.RunStripStep__icon(
          :class="{ 'RunStripStep__icon--swirl': isRunning }"
        ) {{ stepIcon }}
        .RunStripStep__label {{ stepId }}

      .RunStripStep__overlay(v-if="show" :class="getStateClassesFor('overlay')")
        .RunStripStep__infoRow
          .RunStripStep__name {{ step.name }}

        .RunStripStep__actionsRow
          // Abort running
          .RunStripStep__button(
            v-if="isRunning"
            @click="abortStep"
          )
            i.material-icons cancel

        // Run or add to running queue
        .RunStripStep__actionsRow
          .RunStripStep__button(
            v-if="!isQueued && !isRunning"
            @click="queueStepToRun"
          )
            i.material-icons play_arrow

          // Remove from runing queue
          .RunStripStep__button(
            v-if="isAnyRunning && isQueued && !isRunning"
            @click="abortStep"
          )
            i.material-icons highlight_off

          // Run all steps from start to here
          .RunStripStep__button(
            v-if="!isAnyRunning"
            @click="runStepsFromStart"
          )
            i.material-icons keyboard_capslock

          // Run all steps from here to end
          .RunStripStep__button(
            v-if="!isAnyRunning"
            @click="runStepsFromHere"
          )
            i.material-icons(style="transform: rotate(180deg);") keyboard_capslock

          .RunStripStep__spacer

          // Run all steps from here to end
          .RunStripStep__button(
            v-if="!isAnyRunning"
            @click="editStepSettings"
          )
            i.material-icons settings
</template>

<script>
import http from '../../../http';
import stepper from '../../../stepper';
import notebook from '../../../notebook';

function onToggleShow(showState) {
  clearTimeout(this.delayTimeout);
  this.delayTimeout = setTimeout(() => {
    this.show = showState;
  }, showState ? 0 : 50);
}

function stepId() {
  const index = (this.index + 1).toString().padStart(2, '0');
  return `S${index}`;
}

/**
 * Function used to focus the notebook on this step in response to user
 * interaction with the step.
 */
function focusOnStep() {
  this.$emit('focus', { step: this.step, index: this.index });
  this.show = !this.show;

  // If this step is already selected then just refocus on it and
  // skip the network activity.
  const selectedStep = stepper.getSelectedStep();
  if (selectedStep && selectedStep.name === this.step.name) {
    return notebook.scrollToStep(this.step.name);
  }

  this.warmingSelected = true;
  return http
    .execute(`steps select "${this.step.name}`)
    .then((response) => {
      this.$store.commit('project', response.data.data.project);
      this.warmingSelected = false;
      http.markStatusDirty();
    });
}

function abortStep() {
  if (!this.isRunning) {
    stepper.removeStepFromQueue(this.step.name);
    return Promise.resolve();
  }

  stepper.clearQueue();
  this.$emit('aborting', { step: this.step, index: this.index });
  return http.abortExecution()
    .then(response => this.$emit('aborted', { response, step: this.step, index: this.index }));
}

/**
 * Returns a boolean indicating whether or not this step is in the run execution
 * queue.
 */
function isQueued() {
  return stepper.isStepQueued(this.step.name);
}

/**
 * Queues this step to run. If no other steps are running, this step will be
 * run immediately instead. If the step is already running or already queued
 * the action will be ignored for idempotency.
 */
function queueStepToRun() {
  this.show = false;
  stepper.queueStepToRun(this.step.name);
  http.markStatusDirty();
  return Promise.resolve();
}

function runStepsFromStart() {
  this.show = false;
  const steps = (this.$store.getters.project || {}).steps || [];
  const runPromise = http.runStep(steps[0].name);
  stepper.addToQueue(steps.slice(1, this.index + 1).map(s => s.name));
  return runPromise;
}

function runStepsFromHere() {
  this.show = false;
  const steps = (this.$store.getters.project || {}).steps || [];
  const runPromise = http.runStep(this.step.name);
  stepper.addToQueue(steps.slice(this.index + 1).map(s => s.name));
  return runPromise;
}

function state() {
  const { step } = this;
  const states = [
    { id: 'unknown', value: !step },
    { id: 'queued', value: this.isQueued },
    { id: 'running', value: this.isRunning },
    { id: 'muted', value: step.status.muted },
    { id: 'error', value: step.status.error },
    { id: 'dirty', value: step.status.run && step.status.dirty },
    { id: 'clean', value: step.status.run },
    { id: 'untouched', value: true },
  ];
  return states.filter(s => s.value)[0];
}

function isState(...args) {
  return args.reduce((acc, id) => acc || (this.state.id === id), false);
}

function isRunning() {
  return this.$store.getters.runningStepName === this.step.name || this.step.status.running;
}

function isAnyRunning() {
  return this.isRunning || this.$store.getters.running;
}

function editStepSettings() {
  this.$emit('settings', { step: this.step });
}

/**
 * Returns the icon for the snapshot with the given ID, which is different
 * depending on whether or not it is the currently selected one.
 */
function stepIcon() {
  const mappings = {
    unknown: 'help',
    running: 'sync',
    muted: 'sync_disabled',
    queued: 'query_builder',
    error: 'error',
    untouched: 'radio_button_unchecked',
    dirty: 'sentiment_very_dissatisfied',
    clean: 'sentiment_very_satisfied',
  };
  return mappings[this.state.id];
}

function getStateClassesFor(elementName) {
  const { step } = this;
  const element = elementName && elementName.length > 0 ? `__${elementName}` : '';
  const mainClass = `RunStripStep${element}--${this.state.id}`;
  const selectedClass = `${mainClass}Selected`;
  const isSelected = this.warmingSelected || step.status.selected;
  return isSelected ? [selectedClass] : [mainClass];
}

function data() {
  return {
    show: false,
    // Used to override selection temporarily while background command execution
    // is underway. This prevents a lag in state response from the ui.
    warmingSelected: false,
    delayTimeout: null,
  };
}

export default {
  name: 'RunStripStep',
  props: {
    step: { type: Object, default: () => {} },
    index: { type: Number, default: 0 },
  },
  data,
  computed: {
    stepId,
    stepIcon,
    isAnyRunning,
    isRunning,
    isQueued,
    state,
  },
  methods: {
    abortStep,
    editStepSettings,
    focusOnStep,
    getStateClassesFor,
    isState,
    onToggleShow,
    queueStepToRun,
    runStepsFromHere,
    runStepsFromStart,
  },
};
</script>

<style scoped lang="scss">
  @import 'stateStyles/unknown';
  @import 'stateStyles/untouched';
  @import 'stateStyles/dirty';
  @import 'stateStyles/clean';
  @import 'stateStyles/error';
  @import 'stateStyles/running';
  @import 'stateStyles/queued';
  @import '../../../Variables';

  .RunStripStep {
    padding: 0.25em;
    position: relative;
    user-select: none;

    &__box {
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;

      &:hover {
        opacity: 0.7;
      }
    }

    &__icon {
      margin-right: 0.2em;

      &--swirl {
        animation: swirling-keyframes;
        animation-duration: 1s;
        animation-timing-function: ease-out;
        animation-iteration-count: infinite;
      }

      @keyframes swirling-keyframes {
        0% { opacity: 0.01; -webkit-transform: rotate(0deg);}
        50% {opacity: 0.99; -webkit-transform: rotate(-90deg);}
        100% {opacity: 0.01; -webkit-transform: rotate(-180deg);}
      }
    }

    &__label {
      font-size: 0.8em;
    }

    &__overlay {
      /* See stateStyles for additional styling */
      position: absolute;
      top: -1em;
      left: 3.2em;
      min-width: 240px;
      z-index: $menu-z-index;
      padding: 0.25em;
    }

    &__infoRow {
      display: flex;
      align-items: center;
      padding: 0 0.25em;
    }

    &__name {
      font-size: 0.9em;
      overflow: hidden;
    }

    &__actionsRow {
      display: flex;
      align-items: center;
      margin-top: 0.25em;
    }

    &__spacer {
      flex: 1;
    }

    &__button {
      cursor: pointer;
      padding: 0 0.25em;

      &:hover {
        opacity: 0.7;
      }
    }
  }
</style>
