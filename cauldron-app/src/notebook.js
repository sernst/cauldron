import utils from './utils';
import store from './store';

/**
 * The URL to load as part of displaying the project.
 */
function getUrl() {
  const { origin } = window.location;
  const myPath = window.location.pathname.replace('app/project', 'notebook');
  return `${origin}${myPath}/display.html`;
}

function getIframe() {
  return document.querySelector('.Notebook__frame');
}

function refresh() {
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

function applyStepModifications(renames, changes, stepName) {
  const isUnmodified = (
    Object.keys(renames || {}).length === 0
    && (changes || []).length === 0
  );

  if (isUnmodified) {
    return Promise.resolve();
  }

  const cauldron = getCauldronObject();

  return cauldron.processStepRenames(renames || {})
    .then(() => {
      cauldron.processStepUpdates(changes || []);
      return utils.thenWait(500);
    })
    .then(() => {
      if (!stepName && !store.getters.followSteps) {
        // Don't follow steps automatically if the `followSteps` setting isn't true.
        return;
      }

      const steps = (store.getters.project || {}).steps || [];
      const targetSteps = steps
        .filter(s => s.name === stepName)
        .concat(changes.filter(c => c.step).reverse());

      if (targetSteps.length === 0) {
        return;
      }

      const step = targetSteps[0];
      const hasError = (step.status || {}).error;
      scrollToStep(step.name, hasError ? 'error' : 'end');
    });
}

function onLoaded() {
  return new Promise((resolve) => {
    // This first phase waits until the page has loaded to the point of
    // the html script tag having run, which sets up the CAULDRON obect
    // for initial use.
    let retryCount = 0;
    const interval = setInterval(
      () => {
        const cauldron = getCauldronObject();

        // Wait until the cauldron object first becomes available.
        if (!cauldron || !cauldron.on || !cauldron.on.ready) {
          return;
        }

        // If cauldron enters the RUNNING state, which means that the main function
        // has been called, move onto the next on-ready phase.
        if (cauldron.RUNNING) {
          clearInterval(interval);
          resolve(cauldron);
          return;
        }

        // If cauldron has become available but main has not started running yet,
        // keep checking until too much time has passed after which the page should
        // be refreshed to avoid a failure to load.
        retryCount += 1;
        if (retryCount > 10) {
          retryCount = 0;
          refresh();
        }
      },
      200,
    );
  })
    .then(cauldron => cauldron.on.ready);
}

export default {
  applyStepModifications,
  getUrl,
  getCauldronObject,
  getIframe,
  refresh,
  onLoaded,
  scrollToStep,
};
