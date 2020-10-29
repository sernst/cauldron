import axios from 'axios';
import store from './store';
import stepper from './stepper';
import notebook from './notebook';
import exceptions from './exceptions';
import utils from './utils';

const statusCache = {
  lastInvocationTimestamp: 0,
};

function markStatusDirty() {
  store.commit('isStatusDirty', true);
}

/**
 * Mutate store with new errors, deduping as they are added.
 * @param response
 *  The response object returned from a request to the kernel.
 */
function addErrors(response) {
  const responseErrors = ((response || {}).data || {}).errors || [];
  exceptions.addErrors(responseErrors);
}

/**
 * Mutate store with new warnings, deduping as they are added.
 * @param response
 *  The response object returned from a request to the kernel.
 */
function addWarnings(response) {
  const responseWarnings = ((response || {}).data || {}).warnings || [];
  exceptions.addWarnings(responseWarnings);
}

/**
 * Creates an Axios instance configured to communicate with the Cauldron kernel hosting
 * the UI.
 * @returns {AxiosInstance}
 */
function createGateway(timeout) {
  const root = window.location.origin;
  return axios.create({
    baseURL: `${root}/v1/api/`,
    timeout: timeout || 10000,
    headers: {
      'Content-Type': 'application/json',
    },
  });
}

/**
 * Generic GET method endpoint request and response execution.
 * @param endpoint
 * @param timeout
 * @returns {Promise<AxiosResponse>}
 */
function get(endpoint, timeout) {
  return createGateway(timeout)
    .get(endpoint)
    .catch((error) => {
      console.error(`FAILED GET::${endpoint}`, error);
      throw error;
    });
}

function post(endpoint, data, timeout) {
  return createGateway(timeout)
    .post(endpoint, data || {})
    .catch((error) => {
      console.error(`FAILED POST::${endpoint}`, data, error);
      throw error;
    });
}

function execute(command) {
  const prefix = command.split(' ')[0];
  return post(`/command/sync/${prefix}`, { prefix, command }, 30000)
    .then((response) => {
      addErrors(response);
      addWarnings(response);
      return response;
    });
}

function executeAsync(command) {
  const prefix = command.split(' ')[0];
  return post(`/command/async/${prefix}`, { prefix, command })
    .then((response) => {
      addErrors(response);
      addWarnings(response);
      return response;
    });
}

function handleStepRunningError(response) {
  const stepChanges = response.data.data.step_changes || [];
  const hasRunningStepError = (
    !response.data.success
    || (response.data.errors || []).length > 0
    || stepChanges.filter((c) => ((c || {}).step || {}).has_error).length > 0
  );

  if (hasRunningStepError) {
    stepper.clearQueue();
    store.commit('running', false);
    markStatusDirty();
  }

  return hasRunningStepError;
}

function runStep(stepName) {
  store.commit('running', true);
  store.commit('runningStepName', stepName);

  return executeAsync(`run "${stepName}" --print-status`, stepName)
    .then((response) => {
      handleStepRunningError(response);

      const payload = response.data;
      return notebook
        .applyStepModifications(
          payload.data.step_renames,
          payload.data.step_changes,
        )
        .then(() => {
          markStatusDirty();
          return response;
        });
    });
}

/**
 * Update the Vuex store with all of the state information needed to keep the
 * UI in sync with the backend. A debounce argument can optionally be specified
 * with a number of milliseconds since the last update to prevent collisions
 * with fast updates.
 *
 * @param debounce
 * @param force
 * @returns {Promise<AxiosResponse>|Promise<{data: *}>}
 */
function updateStatus(debounce = 0, force = false) {
  const lastInvokedMillis = Math.max(statusCache.lastInvocationTimestamp, 0);
  if (debounce > 0) {
    const timestamp = (new Date()).getTime();
    const elapsed = timestamp - lastInvokedMillis;
    if (elapsed < debounce) {
      return Promise.resolve({ data: store.getters.status });
    }
  }

  const forceArg = force ? 'yes' : null;
  const lastTimestamp = (store.getters.status || {}).timestamp || 0;
  const data = { last_timestamp: lastTimestamp, force: forceArg };
  statusCache.lastInvocationTimestamp = (new Date()).getTime();

  return post('/status', data)
    .then((response) => {
      const payload = response.data;

      if (!payload) {
        // If there's no payload something went wrong and it's time to abort.
        return Promise.resolve(response);
      }

      if (!payload.success) {
        // This will force immediate retry to prevent transient failures from
        // causing longer-term synchronization errors with the kernel.
        statusCache.lastInvocationTimestamp = 0;
      }

      const { project, remote } = payload.data;

      // Whether or not an asynchronous command thread is currently running.
      const isActiveAsync = payload.data.is_active_async;

      const steps = (project || {}).steps || [];
      const hasRunningStepError = handleStepRunningError(response);
      const lastHash = (store.getters.status || {}).hash || '';
      const hash = payload.hash || '';

      const runningSteps = steps.filter((s) => s.status.running);
      const running = !hasRunningStepError && runningSteps.length > 0;
      const syncing = ((remote || {}).sync || {}).active;

      // Only update status information if the information has
      // changed since the last update.
      if (lastHash !== hash) {
        store.commit('status', payload);
        store.commit('project', project);
      }

      // Update running status if needed.
      const wasRunning = store.getters.running;
      const shouldBeRunning = (
        syncing
        || running
        || isActiveAsync
        || store.getters.queuedStepsToRun.length > 0
      );
      if (wasRunning !== shouldBeRunning) {
        store.commit('running', shouldBeRunning);
      }

      // Update the running step name if necessary.
      const previousRunningStepName = store.getters.runningStepName;
      const runningStepPossibilities = [
        // If running, use the running steps name.
        running ? runningSteps[0].name : null,
        // If should be running, keep the previous running step name until that
        // is replaced by a new running step.
        shouldBeRunning ? previousRunningStepName : null,
      ];
      const newRunningStepName = runningStepPossibilities
        .reduce((choice, name) => name || choice, null);

      if (previousRunningStepName !== newRunningStepName) {
        store.commit('runningStepName', newRunningStepName);
      }

      // If running has just stopped mark status dirty to capture any post step changes
      // made after the running state change. This helps prevent the final dom updates
      // from mysteriously not appearing in the results.
      if (wasRunning && !shouldBeRunning) {
        markStatusDirty();
      }

      return notebook
        .applyStepModifications(
          payload.data.step_renames,
          payload.data.step_changes,
        )
        .then(() => {
          // If there's a running queue, go ahead and process the next step.
          const shouldRunNextStep = (
            !syncing
            && !running
            && !isActiveAsync
            && store.getters.queuedStepsToRun.length > 0
          );

          if (shouldRunNextStep) {
            const stepName = store.getters.queuedStepsToRun[0];
            store.commit('queuedStepsToRun', store.getters.queuedStepsToRun.slice(1));

            // Add a little bit of a wait to help prevent race conditions before running
            // a new step.
            return utils.thenWait(100)
              .then(() => runStep(stepName))
              .then(() => utils.thenWait(100))
              .then(() => response);
          }

          return response;
        });
    });
}

async function abortExecution() {
  stepper.clearQueue();
  const response = await post('/command/abort');
  addErrors(response);
  addWarnings(response);
  store.commit('running', false);
  markStatusDirty();
  return response;
}

export default {
  abortExecution,
  get,
  post,
  execute,
  executeAsync,
  updateStatus,
  markStatusDirty,
};
