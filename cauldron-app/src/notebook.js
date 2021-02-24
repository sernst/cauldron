import utils from './utils';
import store from './store';

let cacheBuster = Math.round((new Date()).getTime() / 1000);

/**
 * The URL to load as part of displaying the project.
 */
function getUrl() {
  const { origin } = window.location;
  const myPath = window.location.pathname.replace('app/project', 'notebook');
  return `${origin}${myPath}/display.html?no-cache=${cacheBuster}`;
}

/**
 * The URL to display for showing viewer files within the UI.
 *
 * @returns {string}
 */
function getViewUrl() {
  const { view } = store.getters;
  if (!view) {
    return '';
  }

  const { origin } = window.location;
  const myPath = window.location.pathname.replace('/app', '');
  const dataRoot = encodeURIComponent(`${myPath}/cache/${view.id}`);
  return `${origin}${myPath}/notebook/project.html?no-cache=${cacheBuster}&data_root=${dataRoot}`;
}

function getIframe() {
  return document.querySelector('.Notebook__frame');
}

function refresh() {
  cacheBuster = Math.round((new Date()).getTime() / 1000);
  const iframe = getIframe();
  if (iframe) {
    iframe.contentWindow.location.reload();
  }
}

function getCauldronObject() {
  try {
    const iframe = getIframe();
    return ((iframe || {}).contentWindow || {}).CAULDRON;
  } catch (ignore) {
    return null;
  }
}

function scrollToStep(stepName, position) {
  const cauldron = getCauldronObject();
  if (!cauldron) {
    return;
  }

  if (stepName) {
    cauldron.scrollToAnchor(stepName, position);
    return;
  }

  // Find the currently running AND selected step if it exists. That will be
  // where the default focusing will be applied.
  const steps = (store.getters.project || {}).steps || [];
  const targets = steps.filter((s) => {
    const isRunning = s.status.running || s.name === store.getters.runningStepName;
    return isRunning && (s.status.selected || store.getters.followSteps);
  });

  if (targets.length === 0) {
    return;
  }

  const defaultPosition = targets[0].status.error ? 'error' : 'end';
  cauldron.scrollToAnchor(targets[0].name, position || defaultPosition);
}

/**
 * We're only interested in step changes that are actually changes and that
 * occur more recently than the previous one. This filters down the source
 * changes into only significant and meaningful ones.
 *
 * @param changes
 *    The source changes to filter down to meaningful ones.
 * @returns {*}
 *    An array containing the significant changes.
 */
function filterStepChanges(changes) {
  const { previousStepChanges } = store.getters;

  return changes.filter((c) => {
    const previous = previousStepChanges[c.name] || {};

    const newBody = (c.step || {}).body || '';
    const oldBody = (previous.step || {}).body || '';

    // Older Cauldron versions did not all have timestamps in changes, so we
    // use defaults here just in case.
    const newTimestamp = c.timestamp || 1;
    const oldTimestamp = previous.timestamp || 0;

    // If there is no step it's a remove operation and should be handled.
    // Otherwise, make sure the update is meaningful.
    return c.action === 'added'
      || c.action === 'removed'
      || (newBody !== oldBody && newTimestamp > oldTimestamp);
  });
}

/**
 *
 * @param renames
 * @param changes
 * @param stepName
 * @returns {Promise<void>|Promise<T>}
 */
function applyStepModifications(renames, changes, stepName) {
  const newChanges = filterStepChanges(changes || []);
  const isUnmodified = (
    Object.keys(renames || {}).length === 0
    && (newChanges || []).length === 0
  );

  if (isUnmodified) {
    return Promise.resolve();
  }

  const cauldron = getCauldronObject();
  if (!cauldron) {
    return Promise.resolve();
  }

  return cauldron.processStepRenames(renames || {})
    .then(() => {
      cauldron.processStepUpdates(newChanges);

      // Update changes in the store for future reference to prevent insignificant
      // changes to steps where the body does not change from updating the dom and
      // wasting rendering resources.
      const { previousStepChanges } = store.getters;
      const updatedChanges = newChanges
        .reduce((all, c) => Object.assign(all, { [c.name]: c }), {});
      const combinedChanges = { ...previousStepChanges, ...updatedChanges };
      store.commit('previousStepChanges', combinedChanges);

      return utils.thenWait(300);
    })
    .then(() => {
      if (!stepName && !store.getters.followSteps) {
        // Don't follow steps automatically if the `followSteps` setting isn't true.
        return;
      }

      const steps = (store.getters.project || {}).steps || [];
      const targetSteps = steps
        .filter((s) => s.name === stepName)
        .concat(changes.filter((c) => c.step).reverse());

      if (targetSteps.length === 0) {
        return;
      }

      const step = targetSteps[0];
      const hasError = (step.status || {}).error;
      scrollToStep(step.name, hasError ? 'error' : 'end');
    });
}

function onLoaded() {
  return new Promise((resolve, reject) => {
    // This first phase waits until the page has loaded to the point of
    // the html script tag having run, which sets up the CAULDRON obect
    // for initial use.
    let waitCount = 0;
    let retryCount = 0;
    const interval = setInterval(
      () => {
        const cauldron = getCauldronObject();
        const { project, view } = store.getters;

        if (!project && !view) {
          clearInterval(interval);
          reject();
          return;
        }

        // Wait until the cauldron object first becomes available and refresh if
        // it doesn't become available in a reasonable amount of time.
        if (!cauldron || !cauldron.on || !cauldron.on.ready) {
          waitCount += 1;
          if (waitCount > 10) {
            waitCount = 0;
            console.warn('Notebook load wait timeout reached. Refreshing...');
            refresh();
          }

          return;
        }

        // If cauldron enters the RUNNING state, which means that the main function
        // has been called, move onto the next on-ready phase.
        if (cauldron.RUNNING) {
          clearInterval(interval);
          cauldron.on.ready.then(() => resolve(cauldron));
          return;
        }

        // If cauldron has become available but main has not started running yet,
        // keep checking until too much time has passed after which the page should
        // be refreshed to avoid a failure to load.
        retryCount += 1;
        if (retryCount > 10) {
          retryCount = 0;
          console.warn('Notebook load running timeout reached. Refreshing...');
          refresh();
        }
      },
      200,
    );
  });
}

export default {
  applyStepModifications,
  getUrl,
  getViewUrl,
  getCauldronObject,
  getIframe,
  refresh,
  onLoaded,
  scrollToStep,
};
