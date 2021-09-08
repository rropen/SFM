const webpack = require(“webpack”);

module.exports = {

publicPath: process.env.NODE_ENV === “production” ? “” : “/”,

// devServer: {

// proxy: “http://souqchat.localhost/api/”

// },

transpileDependencies: [“vuetify”],

configureWebpack: {

// Set up all the aliases we use in our app.

plugins: [

  new webpack.optimize.LimitChunkCountPlugin({

    maxChunks: 20

  })

]
},
css: {

// Enable CSS source maps.

sourceMap: process.env.NODE_ENV !== "production"
}
};