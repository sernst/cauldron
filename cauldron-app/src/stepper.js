import store from './store';

function getStep(stepName) {
  const steps = (store.getters.project || {}).steps || [];
  const matches = steps.filter((s) => s.name === stepName);
  return matches.length > 0 ? matches[0] : null;
}

function getSelectedStep() {
  const steps = (store.getters.project || {}).steps || [];
  const matches = steps.filter((s) => s.status.selected);
  return matches.length > 0 ? matches[0] : null;
}

function isStepQueued(stepName) {
  return store.getters.queuedStepsToRun.filter((s) => s === stepName).length > 0;
}

function isStepRunning(stepName) {
  const step = getStep(stepName);
  return step !== null ? step.status.running : false;
}

function queueStepToRun(stepName) {
  if (isStepQueued(stepName) || isStepRunning(stepName)) {
    return;
  }

  const updated = store.getters.queuedStepsToRun.concat([stepName]);
  store.commit('queuedStepsToRun', updated);
}

function removeStepFromQueue(stepName) {
  const queue = store.getters.queuedStepsToRun.concat();
  const index = queue.indexOf(stepName);

  if (index < 0) {
    return false;
  }

  queue.splice(index, 1);
  store.commit('queuedStepsToRun', queue);
  return true;
}

function addToQueue(stepNames) {
  const queue = store.getters.queuedStepsToRun.concat();
  const newSteps = stepNames.filter((s) => queue.indexOf(s) < 0);

  if (newSteps.length > 0) {
    store.commit('queuedStepsToRun', queue.concat(newSteps));
  }
}

function setStepRunning(stepName) {
  store.commit('runningStepName', stepName);
  store.commit('running', stepName !== null);
}

function clearQueue() {
  store.commit('queuedStepsToRun', []);
}

export default {
  addToQueue,
  clearQueue,
  getStep,
  getSelectedStep,
  isStepQueued,
  isStepRunning,
  queueStepToRun,
  removeStepFromQueue,
  setStepRunning,
};
