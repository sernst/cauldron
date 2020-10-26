const path = require('path');

// === WARNING: STATIC DEVELOPMENT PURPOSES ONLY ===
// This file is not used for webpack compilation. Instead it is a static
// representation of the webpack.config.js that is generated from the
// vue.config.js that is needed to help support statically-determined
// webpack behaviors within the code during development. For the moment,
// this is the recommended way of handling this until dynamic webpack
// configuration is more widely adopted within Vuejs projects.

module.exports = {
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
};
