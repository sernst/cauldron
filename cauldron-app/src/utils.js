

function thenWait(elapsedMilliseconds, args) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(args);
    }, elapsedMilliseconds);
  });
}

export default { thenWait };
