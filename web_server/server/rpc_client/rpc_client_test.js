var client = require('./rpc_client');

client.add(1, 2, function(res) {
  console.assert(res == 3);
});
