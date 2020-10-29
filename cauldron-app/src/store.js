import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

function createEmptyStatus() {
  return { data: { success: true, timestamp: 0 } };
}

export default new Vuex.Store({
  state: {
    followSteps: true,
    errors: [],
    warnings: [],
    isStatusDirty: true,
    project: null,
    queuedStepsToRun: [],
    running: false,
    runningStepName: null,
    savingFile: false,
    status: createEmptyStatus(),
    loadingMessages: [],
    isNotebookLoading: false,
    previousStepChanges: {},
  },
  mutations: {
    followSteps(state, value) {
      state.followSteps = value || false;
    },
    errors(state, value) {
      state.errors = value || [];
    },
    warnings(state, value) {
      state.warnings = value || [];
    },
    isStatusDirty(state, value) {
      state.isStatusDirty = value || false;
    },
    project(state, value) {
      state.project = value || null;
    },
    queuedStepsToRun(state, value) {
      state.queuedStepsToRun = value || [];
    },
    running(state, value) {
      state.running = value || false;
    },
    runningStepName(state, value) {
      state.runningStepName = value || null;
    },
    savingFile(state, value) {
      state.savingFile = value || false;
    },
    status(state, value) {
      state.status = value || createEmptyStatus();
    },
    loadingMessages(state, value) {
      state.loadingMessages = value || [];
    },
    isNotebookLoading(state, value) {
      state.isNotebookLoading = value || false;
    },
    previousStepChanges(state, value) {
      state.previousStepChanges = value || {};
    },
  },
  getters: {
    followSteps: (state) => state.followSteps,
    errors: (state) => state.errors,
    warnings: (state) => state.warnings,
    isStatusDirty: (state) => state.isStatusDirty,
    project: (state) => state.project,
    queuedStepsToRun: (state) => state.queuedStepsToRun,
    running: (state) => state.running,
    runningStepName: (state) => state.runningStepName,
    savingFile: (state) => state.savingFile,
    status: (state) => state.status,
    view: (state) => ((state.status || {}).data || {}).view || null,
    loadingMessages: (state) => state.loadingMessages,
    isNotebookLoading: (state) => state.isNotebookLoading,
    previousStepChanges: (state) => state.previousStepChanges,
  },
});
