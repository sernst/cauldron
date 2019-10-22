const path = require('path');

module.exports = {
  configureWebpack: { context: path.resolve(__dirname) },
  outputDir: '../cauldron/resources/app',
  publicPath: '/v1/app/',
  assetsDir: 'assets',
};
