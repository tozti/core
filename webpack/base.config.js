const path = require('path')
const webpack = require('webpack')
const ExtractPlugin = require('extract-text-webpack-plugin')
const CopyWebpackPlugin = require('copy-webpack-plugin')

// Custom loader for static assets
const fileLoader = {
  loader: 'file-loader',
  options: {
    name: '[path][name].[ext]',
    context: path.resolve(__dirname, '../assets'),
    publicPath: "/static/core/",
  }
}

// Webpack configuration
module.exports = {

  entry: {
    launch: './client/launch.js',
    bootstrap: './client/bootstrap.js',
    style: './assets/sass/style.scss',
  },

  output: {
    path: path.resolve(__dirname, '../dist/'),
    filename: '[name].js',
  },

  plugins: [
    new ExtractPlugin('css/[name].css'),
    new CopyWebpackPlugin([
      { from: 'assets/img/', to: 'img/', }
    ])
  ],

  module: {
    rules: [
      {
        test: /\.css$/,
        use: ExtractPlugin.extract(['css-loader']),
      },
      {
        test: /\.scss$/,
        use: ExtractPlugin.extract({
          fallback: 'vue-style-loader',
          use: ['css-loader', 'sass-loader'],
        })
      },
      {
        test: /\.sass$/,
        use: ExtractPlugin.extract({
          fallback: 'vue-style-loader',
          use: ['css-loader', 'sass-loader?indentedSyntax'],
        })
      },
      {
        test: /\.vue$/,
        loader: 'vue-loader',
        options: {
          loaders: {
            'css': ExtractPlugin.extract({
              fallback: 'vue-style-loader',
              use: ['css-loader'],
            }),
            'scss': ExtractPlugin.extract({
              fallback: 'vue-style-loader',
              use: ['css-loader', 'sass-loader'],
            }),
            'sass': ExtractPlugin.extract({
              fallback: 'vue-style-loader',
              use: ['css-loader', 'sass-loader?indentedSyntax'],
            })
          }
        }
      },
      {
        test: /\.(png|jpg|gif|svg)$/,
        use: [fileLoader, 'image-webpack-loader'],
      },
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/,
        use: [fileLoader]
      }
    ]
  },

  resolve: {
    extensions: ['*', '.js', '.vue', '.json'],
    alias: {
      assets: path.resolve(__dirname, '../assets')
    },
  },

  externals: {
    vue: 'Vue',
    tozti: 'tozti',
    buefy: 'Buefy'
  }
}
