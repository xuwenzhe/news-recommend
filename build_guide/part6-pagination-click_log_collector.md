# Part 6 - Pagination + Click Log Collector

## Step 1. `operations`

Create `backend_server/operations.py`

```python
import json
import os
import pickle # Make JSON(dict) becomes String that could be read by Redis
import random
import redis
import sys

from bson.json_util import dumps
from datetime import datetime

# import common package in parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

import mongodb_client

REDIS_HOST = "localhost"
REDIS_PORT = 6379

NEWS_TABLE_NAME = "news"
CLICK_LOGS_TABLE_NAME = 'click_logs'

NEWS_LIMIT = 100
NEWS_LIST_BATCH_SIZE = 10 # number of news sent everytime when client requests
USER_NEWS_TIME_OUT_IN_SECONDS = 60

redis_client = redis.StrictRedis(REDIS_HOST, REDIS_PORT, db=0)


def getOneNews():
    """ Test method to get one news. """
    res = mongodb_client.get_db()['news'].find_one()
    return json.loads(dumps(res))


def getNewsSummariesForUser(user_id, page_num):
    page_num = int(page_num)
    begin_index = (page_num - 1) * NEWS_LIST_BATCH_SIZE
    end_index = page_num * NEWS_LIST_BATCH_SIZE

    # The final list of news to be returned.
    sliced_news = []

    if redis_client.get(user_id) is not None:
        news_digests = pickle.loads(redis_client.get(user_id))

        # If begin_index is out of range, this will return empty list;
        # If end_index is out of range (begin_index is within the range), this
        # will return all remaining news ids.
        sliced_news_digests = news_digests[begin_index:end_index]
        db = mongodb_client.get_db()
        sliced_news = list(db[NEWS_TABLE_NAME].find({'digest':{'$in':sliced_news_digests}}))
    else:
        db = mongodb_client.get_db()
        total_news = list(db[NEWS_TABLE_NAME].find().sort([('publishedAt', -1)]).limit(NEWS_LIMIT))
        total_news_digests = [x['digest'] for x in total_news]

        redis_client.set(user_id, pickle.dumps(total_news_digests))
        redis_client.expire(user_id, USER_NEWS_TIME_OUT_IN_SECONDS)

        sliced_news = total_news[begin_index:end_index]


    for news in sliced_news:
        # Remove text field to save bandwidth.
        del news['text']
        if news['publishedAt'].date() == datetime.today().date():
            news['time'] = 'today'
    return json.loads(dumps(sliced_news))

```

Create test file `backend_server/operations_test.py`

```python
import operations

def test_getOneNews_basic():
    news = operations.getOneNews()
    print(news)
    assert news is not None
    print("test_getOneNews_basic passed!")

def test_getNewsSummariesForUser_basic():
    news = operations.getNewsSummariesForUser('test', 1)
    assert len(news) > 0
    print('test_getNewsSummariesForUser_basic passed!')


def test_getNewsSummariesForUser_pagination():
    news_page_1 = operations.getNewsSummariesForUser('test', 1)
    news_page_2 = operations.getNewsSummariesForUser('test', 2)

    assert len(news_page_1) > 0
    assert len(news_page_2) > 0 

    digests_page_1_set = set(news['digest'] for news in news_page_1)
    digests_page_2_set = set(news['digest'] for news in news_page_2)

    assert len(digests_page_1_set.intersection(digests_page_2_set)) == 0

    print('test_getNewsSummariesForUser_pagination passed!')
    


if __name__ == "__main__":
    test_getOneNews_basic()
    test_getNewsSummariesForUser_basic()
    test_getNewsSummariesForUser_pagination()
```

Update `backend_server/service.py`

```python
def get_one_news():
    """ Test method to get one news. """
    print("get_one_news is called")
    return operations.getOneNews()

def get_news_summaries_for_user(user_id, page_num):
    print("get_news_summaries_for_user is called with %s and %s" %(user_id, page_num))
    return operations.getNewsSummariesForUser(user_id, page_num)
    
...

RPC_SERVER.register_function(get_one_news, 'getOneNews')
RPC_SERVER.register_function(get_news_summaries_for_user, 'getNewsSummariesForUser')
```

To test,

```
python3 operations_test.py
```

## Step 2. Web Server
Update `web_server/client/src/NewsPanel/NewsPanel.js`

```javascript
  constructor() {
    super();
    this.state = {news: null, pageNum: 1, loadedAll: false};
  }
   
  loadMoreNews() {
    console.log('Actually triggered loading more news.')
    if (this.state.loadedAll == true) {
      return;
    }

    // refer to newsAPI at web_server/server/routes/news.js
    const news_url = 'http://' + window.location.hostname
                   + ':3000/news/userId=' + Auth.getEmail()
                   + "&pageNum=" + this.state.pageNum;

    // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/encodeURI
    const request = new Request(encodeURI(news_url), {
      method: 'GET',
      headers: {
        'Authorization': 'bearer ' + Auth.getToken(),
      },
    });

    fetch(request)
      .then(res => res.json())
      .then(news_list => {
        // render-cycle explanation
        // https://stackoverflow.com/a/24719289
        if (!news_list || news_list.length == 0) {
          this.setState({loadedAll:true});
        }
        this.setState({
          news: this.state.news ? this.state.news.concat(news_list) : news_list,
          pageNum: this.state.pageNum + 1
        });
      })
  }
```

Update `web_server/server/routes/news.js`

```javascript
var rpc_client = require('../rpc_client/rpc_client');

/* GET news list. */
router.get('/userId=:userId&pageNum=:pageNum', function(req, res, next) {
  console.log('Fetching news...');
  userId = req.params['userId'];
  pageNum = req.params['pageNum'];

  rpc_client.getNewsSummariesForUser(userId, pageNum, function(response) {
    res.json(response);
  });
});
```

Update `web_server/server/rpc_client/rpc_client.js`

```javascript
// Get news summaries for a user
function getNewsSummariesForUser(user_id, page_num, callback) {
  client.request('getNewsSummariesForUser', [user_id, page_num], function(err, response) {
  	if (err) throw err;
  	console.log(response);
  	callback(response.result);
  });
}

module.exports = {
	add: add,
	getNewsSummariesForUser: getNewsSummariesForUser
};
```

Update `web_server/server/rpc_client/rpc_client_test.js`

```javascript
// invoke "getNewsSummariesForUser"
client.getNewsSummariesForUser('test_user', 1, function(response) {
  console.assert(response != null);
});
```

Now start the backend server (`python3 service.py`) and run the rpc test (`node rpc_client_test.js`)!

## Step 3. Log Processor

Update `web_server/server/src/NewsCard/NewsCard.js`

```javascript
import Auth from '../Auth/Auth'; // log processor

  redirectToUrl(url, event) {
    // default: redirecting at the current page
    event.preventDefault();
    // send to log processor
    this.sendClickLog();
    window.open(url, '_blank');
  }
  sendClickLog() {
    const url = 'http://' + window.location.hostname + ':3000'
              + '/news/userId=' + Auth.getEmail()
              + '&newsId=' + this.props.news.digest;
    const request = new Request(encodeURI(url), {
      method: 'POST',
      headers: {
        'Authorization': 'bearer ' + Auth.getToken(),
      }
    });
    fetch(request);
  }
```

Update `web_server/server/rpc_client/rpc_client.js`

```javascript
function logNewsClickForUser(userId, newsId) {
  client.request('logNewsClickForUser', [userId, newsId], function(err, response) {
  	if (err) throw err;
  	console.log(response.result);
  });
}

module.exports = {
	add: add,
	getNewsSummariesForUser: getNewsSummariesForUser
	logNewsClickForUser: logNewsClickForUser
};
```

Update `web_server/server/routes/news.js`

```javascript
/* Log news click. */
router.get('/userId=:userId&newsId=:newsId', function(req, res, next) {
  console.log('Logging news click...');
  userId = req.params['userId'];
  newsId = req.params['newsId'];

  rpc_client.logNewsClickForUser(userId, newsId);
  res.status(200);
});
```

Update `backend_server/service.py`

```python
def log_news_click_for_user(user_id, news_id):
    print("log_news_click_for_user is called with %s and %s" %(user_id, news_id))
    return operations.log_news_click_for_user(user_id, news_id)
...
RPC_SERVER.register_function(log_news_click_for_user, 'logNewsClickForUser')
```

Update `backend_server/operations.py`

```python
from cloudAMQP_client import CloudAMQPClient

LOG_CLICKS_TASK_QUEUE_URL = ""
LOG_CLICKS_TASK_QUEUE_NAME = "tap-news-log-clicks-task-queue"

cloudAMQP_client = CloudAMQPClient(LOG_CLICKS_TASK_QUEUE_URL, LOG_CLICKS_TASK_QUEUE_NAME)


def log_news_click_for_user(user_id, news_id):
	message = {'userId': user_id, 'newsId': news_id, 'timestamp': str(datetime.utcnow())}
    cloudAMQP_client.sendMessage(message)
```