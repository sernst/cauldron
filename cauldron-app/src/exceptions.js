import store from './store';

// These are error codes that should not result in the display of the
// error overlay because they are displayed in other ways within
// the application/notebook.
const IGNORED_ERROR_CODES = ['EXECUTION_ERROR'];

/**
 * Mutate store with new errors, deduping as they are added.
 * @param errors
 *  An array of errors to add to the stored errors for display.
 */
function addErrors(errors) {
  const existing = store.getters.errors.concat();
  const existingCodes = existing.map(e => e.code).concat(IGNORED_ERROR_CODES);
  const newErrors = (errors || []).filter(e => existingCodes.indexOf(e.code) === -1);

  if (newErrors) {
    store.commit('errors', existing.concat(newErrors));
  }
}

function addError(error) {
  return addErrors([error]);
}

/**
 * Mutate store with new warnings, deduping as they are added.
 * @param warnings
 *  The response object returned from a request to the kernel.
 */
function addWarnings(warnings) {
  const existingWarnings = store.getters.warnings.concat();
  const existingCodes = existingWarnings.map(e => e.code);
  const newWarnings = (warnings || []).filter(e => existingCodes.indexOf(e.code) === -1);

  if (newWarnings) {
    store.commit('warnings', existingWarnings.concat(newWarnings));
  }
}

function addWarning(warning) {
  return addWarnings([warning]);
}

export default {
  addErrors,
  addError,
  addWarnings,
  addWarning,
};
