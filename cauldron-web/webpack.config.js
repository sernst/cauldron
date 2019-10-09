const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CopyPlugin = require('copy-webpack-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const WebpackShellPlugin = require('webpack-shell-plugin');

module.exports = {
  entry: './src/project.js',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'project.js'
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader'
        }
      },
      {
        test: /\.s[ac]ss$/i,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          'sass-loader'
        ]
      },
      {
        test: /\.(png|svg|jpg|gif)$/i,
        loader: 'file-loader',
        options: {
          name: 'assets/[name].[ext]',
        }
      },
      {
        test: /\.html$/,
        loader: 'file-loader',
        options: {
          name: '[name].[ext]',
        }
      },
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/i,
        loader: 'file-loader',
        options: {
          name: 'assets/fonts/[name].[ext]',
        }
      },
    ]
  },
  plugins: [
    new MiniCssExtractPlugin({ filename: 'project.css' }),
    new CopyPlugin([
      { from: 'src/project.html', to: 'project.html' },
    ]),
    // Removes all dist/ files before build
    new CleanWebpackPlugin(),
    // Shell script execution
    new WebpackShellPlugin({
      onBuildEnd: ['python deploy.py']
    }),
  ]
};
