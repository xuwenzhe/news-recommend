// main.js provides a 'connect' function to easily access to mongoDB atlas
// learn nore about using mongoose at: https://youtu.be/WDrU305J1yw

const mongoose = require('mongoose');

module.exports.connect = uri => {
  mongoose.connect(uri);
  mongoose.connection.on('error', err => {
  	console.error(`Mongoose connection error: ${err}`);
  	process.exit(1);
  });
  // load models
  require('./user');
};