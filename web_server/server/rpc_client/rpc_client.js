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

// Get news summaries for a user
function getNewsSummariesForUser(user_id, page_num, callback) {
  client.request('getNewsSummariesForUser', [user_id, page_num], function(err, response) {
  	if (err) throw err;
  	console.log(response);
  	callback(response.result);
  });
}

function logNewsClickForUser(userId, newsId) {
  client.request('logNewsClickForUser', [userId, newsId], function(err, response) {
  	if (err) throw err;
  	console.log(response.result);
  });
}

module.exports = {
	add: add,
	getNewsSummariesForUser: getNewsSummariesForUser,
	logNewsClickForUser: logNewsClickForUser
};