# Part 4 - MongoDB and RabbitMQ

https://github.com/joshmarshall/jsonrpclib

https://github.com/tcalmant/jsonrpclib/


## Step 1. install `brew`, `python3`

Install `brew`

```
# https://brew.sh
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

Install `python3`

```
brew install python3
```

Create virtual environment for this project and then activate it.

```
python3 -m venv ~/.virtualenvs/cs503_env
source ~/.virtualenvs/cs503_env/bin/activate
```

Here are some useful links:

* [compare](https://stackoverflow.com/a/32530866) `pip install` and `brew install`
* [python3 and venv](https://wsvincent.com/install-python3-mac/)
* [venv](https://stackoverflow.com/a/30233408)


## Step 2. Backend Server - RPC server

Install `jsonrpclib`

```
pip3 install jsonrpclib-pelix
```

Base on [this template](https://github.com/tcalmant/jsonrpclib/), setup our first RPC server.

Create `backend_server/service.py`

```python
import logging

from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer

SERVER_HOST = 'localhost'
SERVER_PORT = 4040

logger_format = '%(asctime)s - %(message)s'
logging.basicConfig(format = logger_format)
logger = logging.getLogger('backend_service')
logger.setLevel(logging.DEBUG)

def add(num1, num2):
	"""Test Method"""
	# doc_string
	# https://www.geeksforgeeks.org/python-docstrings/
	logger.debug('Add is called with %d and %d', num1, num2);
	return num1 + num2



server = SimpleJSONRPCServer((SERVER_HOST, SERVER_PORT))
server.register_function(add, 'add')


logger.info('Starting RPC server on %s:%d', SERVER_HOST, SERVER_PORT)
server.serve_forever()
```

After starting the backend server (`python3 service.py`), use `Postman` to test

```
{
	"jsonrpc": "2.0",
	"id": 99,
	"method": "add",
	"params": [99,3]
}
```

Result should be:

```
{
    "result": 102,
    "id": 99,
    "jsonrpc": "2.0"
}
```

## Step 3. Node Server - RPC Client

Create `web_server/server/rpc_client/rpc_client.js`

```javascript
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
```

Create `web_server/server/rpc_client/rpc_client_test.js`.

```javascript
var client = require('./rpc_client');

client.add(1, 2, function(res) {
  console.assert(res == 3);
});
```

Test rpc client

```
node rpc_client_test.js
```


## Step 3. Local MongoDB

Install [MongoDB](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-os-x/#install-mongodb-community-edition) via brew.

[Run](https://stackoverflow.com/a/41349186) MongoDB service

```
brew services start mongodb-community@4.0
```

Basic shell commands

```
> show dbs
> use tap-news
> show collections
> db.news.find().pretty()
```

Export MongoDB data to file and Import file as MongoDB data using `mongoexport` and `mongoimport` tools

```
mongoexport --db tap-news --collection news --out demo_news.json
mongoimport --db test --collection news --file demo_news.json
mongoimport --db tap-news --collection news --file demo_news.json
```

[`pymongo`](https://api.mongodb.com/python/current/tutorial.html) is a python tool to work with MongoDB.

Install `pymongo`

```
pip3 install pymongo
```

Create `backend_server/utils/mongodb_client` util file

```python
from pymongo import MongoClient

MONGO_DB_HOST = 'localhost'
MONGO_DB_PORT = 27017
DB_NAME = 'tap-news'

client = MongoClient(MONGO_DB_HOST, MONGO_DB_PORT)

# singleton
def get_db(db=DB_NAME):
	db = client[db]
	return db
```

And util test file `backend_server/utils/mongodb_client_test`

```python
import mongodb_client as client

def test_basic():
	db = client.get_db('test')
	db.test.drop()
	assert db.test.count() == 0

	db.test.insert({'test': 1})
	assert db.test.count() == 1

	db.test.drop()
	assert db.test.count() == 0

	print('test basic passed!')

if __name__ == '__main__':
	test_basic()
```

```
python3 mongodb_client_test.py
```

## Step 4. CloudAMQP

Install [`pika`](https://pika.readthedocs.io/en/stable/)

```
pip3 install pika
```

Create AMQP instances at [CloudAMQP](https://www.cloudamqp.com). The `AMQP URL` should be private and unique to our backend_server.

Create `backend_server/utils/cloudAMQP_client.py`

```python
import json
import logging
import pika

logger_format = '%(asctime)s - %(message)s'
logging.basicConfig(format = logger_format)
logger = logging.getLogger('cloud_amqp_client')
logger.setLevel(logging.DEBUG)

class CloudAMQPClient:
	def __init__(self, cloud_amqp_url, queue_name):
		self.cloud_amqp_url = cloud_amqp_url
		self.queue_name = queue_name
		self.params = pika.URLParameters(cloud_amqp_url)
		self.params.socket_timeout = 3
		self.connection = pika.BlockingConnection(self.params)
		self.channel = self.connection.channel()
		self.channel.queue_declare(queue=queue_name)

	# Send a message, basic_publish example
	def sendMessage(self, message):
		self.channel.basic_publish(exchange='',
								   routing_key=self.queue_name,
								   body=json.dumps(message))
		logging.debug("[x] Sent message to %s:%s", self.queue_name, message)

	# Get a message, basic_get example
	def getMessage(self):
		method_frame, header_frame, body = self.channel.basic_get(self.queue_name)
		if method_frame:
			logging.debug("[x] Received message to %s:%s", self.queue_name, body)
			self.channel.basic_ack(method_frame.delivery_tag) # verify received!
			return json.loads(body.decode('utf-8'))
		else:
			logging.debug('No message returned.')
			return None

	# BlockingConnection.sleep is a safer way to sleep than time.sleep(). This
	# will repond to server's heartbeat.
	def sleep(self, seconds):
		self.connection.sleep(seconds)
```

Create `backend_server/utils/cloudAMQP_client_test.py`

```python
from cloudAMQP_client import CloudAMQPClient

CloudAMQP_URL = "[your cloudAMQP instance url]"
TEST_QUEUE_NAME = "test"

def test_basic():
  client = CloudAMQPClient(CloudAMQP_URL,TEST_QUEUE_NAME )

  sentMsg = {"test":"test"}
  client.sendMessage(sentMsg)

  client.sleep(5)

  reveivedMsg = client.getMessage()

  assert sentMsg == reveivedMsg
  print("test_basic passed!")

if __name__ == "__main__":
  test_basic()
```

```
python3 cloudAMQP_client_test.py 
```


## Step 5. First News API

Add another backend-service test function `getOneNews()` in our `service.py`

Update `backend_server/service.py`

```python
import logging
import os
import sys
import json
from bson.json_util import dumps
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer

# import util package in parent dir
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

import mongodb_client

SERVER_HOST = 'localhost'
SERVER_PORT = 4040

logger_format = '%(asctime)s - %(message)s'
logging.basicConfig(format = logger_format)
logger = logging.getLogger('backend_service')
logger.setLevel(logging.DEBUG)

def getOneNews():
	""" Test method to get one news. """
	res = mongodb_client.get_db()['news'].find_one()
	return json.loads(dumps(res))


server = SimpleJSONRPCServer((SERVER_HOST, SERVER_PORT))
server.register_function(getOneNews, 'getOneNews')

logger.info('Starting RPC server on %s:%d', SERVER_HOST, SERVER_PORT)
server.serve_forever()
```

If `demo_news.json` is properly imported, `Postman` with Post-raw request

```
{
	"jsonrpc": "2.0",
	"id": 99,
	"method": "getOneNews",
	"params": []
}
```

should return a news.

## Step 6. Pylint

Install [`pylint`](https://www.pylint.org).

```
pip3 install pylint
```

Check python file coding style.

```
python3 -m pylint service.py
```