const jayson = require('jayson');
 
// create a client
const client = jayson.client.http({
  port: 4040,
  hostname: 'localhost'
});


// middleware utility
function add(a, b, callback) {
  client.request('add', [a, b], function(err, response) {
  	if (err) throw err;
  	console.log(response.result);
  	callback(response.result);
  });
}

module.exports = {
	add: add
};