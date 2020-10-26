const path = require('path');

const packageSettings = require('./package');

module.exports = {
  runtimeCompiler: true,
  outputDir: '../cauldron/resources/app',
  assetsDir: 'assets',
  publicPath: '/v1/app/',
  chainWebpack: (config) => {
    config.resolve.alias.set('@', path.join(__dirname, 'src'));

    config.plugin('define').tap((definitions) => {
      const mode = (process.env.NODE_ENV === 'development') ? 'test' : 'prod';
      const environmentVariables = {
        BUILD_MODE: JSON.stringify(mode),
        UI_VERSION: JSON.stringify(packageSettings.version),
      };

      // Append custom environment variables to the ones that already exist
      // by default as part of the Vue webpack configuration.
      Object.assign(definitions[0]['process.env'], environmentVariables);
      return definitions;
    });
  },
  configureWebpack: { context: path.resolve(__dirname) },
};
