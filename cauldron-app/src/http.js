import axios from 'axios';
import store from './store';
import stepper from './stepper';
import notebook from './notebook';
import exceptions from './exceptions';

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
function createGateway() {
  const root = window.location.origin;
  return axios.create({
    baseURL: `${root}/v1/api/`,
    timeout: 5000,
    headers: {
      'Content-Type': 'application/json',
    },
  });
}

/**
 * Generic GET method endpoint request and response execution.
 * @param endpoint
 * @returns {Promise<AxiosResponse>}
 */
function get(endpoint) {
  return createGateway()
    .get(endpoint)
    .catch((error) => {
      console.error(`FAILED GET::${endpoint}`, error);
      throw error;
    });
}

function post(endpoint, data) {
  return createGateway()
    .post(endpoint, data || {})
    .catch((error) => {
      console.error(`FAILED POST::${endpoint}`, data, error);
      throw error;
    });
}

function execute(command) {
  return post('/command/sync', { command })
    .then((response) => {
      addErrors(response);
      addWarnings(response);
      return response;
    });
}

function executeAsync(command) {
  return post('/command/async', { command })
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
    || stepChanges.filter(c => c.has_error).length > 0
  );

  if (hasRunningStepError) {
    stepper.clearQueue();
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
        throw new Error('Failed to get response from status endpoint.');
      }

      if (!payload.success) {
        // This will force immediate retry to prevent transient failures from
        // causing longer-term synchronization errors with the kernel.
        statusCache.lastInvocationTimestamp = 0;
      }

      const { project } = payload.data;
      const steps = (project || {}).steps || [];
      const hasRunningStepError = handleStepRunningError(response);
      const lastHash = (store.getters.status || {}).hash || '';
      const hash = payload.hash || '';

      if (lastHash === hash) {
        // Abort updating status information if no status information has
        // changed since the last update.
        return response;
      }

      const runningSteps = steps.filter(s => s.status.running);
      const running = !hasRunningStepError && runningSteps.length > 0;

      store.commit('status', payload);
      store.commit('project', project);
      store.commit('running', running || store.getters.queuedStepsToRun.length > 0);

      return notebook
        .applyStepModifications(
          payload.data.step_renames,
          payload.data.step_changes,
        )
        .then(() => {
          // If there's a running queue, go ahead and process the next step.
          if (!running && store.getters.queuedStepsToRun.length > 0) {
            const stepName = store.getters.queuedStepsToRun[0];
            store.commit('queuedStepsToRun', store.getters.queuedStepsToRun.slice(1));
            return runStep(stepName);
          }

          store.commit('runningStepName', running ? runningSteps[0].name : null);
          return response;
        });
    });
}

function abortExecution() {
  return post('/command/abort')
    .then((response) => {
      addErrors(response);
      addWarnings(response);

      const payload = response.data;
      store.commit('project', payload.data.project);
      store.commit('running', false);

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

export default {
  abortExecution,
  get,
  post,
  execute,
  executeAsync,
  updateStatus,
  runStep,
  markStatusDirty,
};
