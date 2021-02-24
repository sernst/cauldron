/** Exposes webpack DefinePlugin variables injected during build. */
function getBuildVar(key) {
  return process.env[key];
}

function thenWait(elapsedMilliseconds, args) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(args);
    }, elapsedMilliseconds);
  });
}

export default { thenWait, getBuildVar };
