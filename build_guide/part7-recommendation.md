# Part 7 - Recommendation

## Step 1. Log Consumer

Create `recommendation_service/click_log_processor.py`

```python
# -*- coding: utf-8 -*-

'''
Time decay model:
If selected:
p = (1-α)p + α
If not:
p = (1-α)p
Where p is the selection probability, and α is the degree of weight decrease.
The result of this is that the nth most recent selection will have a weight of
(1-α)^n. Using a coefficient value of 0.05 as an example, the 10th most recent
selection would only have half the weight of the most recent. Increasing epsilon
would bias towards more recent results more.
'''

import news_classes
import os
import sys

# import common package in parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

import mongodb_client
from cloudAMQP_client import CloudAMQPClient

# Don't modify this value unless you know what you are doing.
NUM_OF_CLASSES = 8
INITIAL_P = 1.0 / NUM_OF_CLASSES
ALPHA = 0.1

SLEEP_TIME_IN_SECONDS = 1

LOG_CLICKS_TASK_QUEUE_URL = ""
LOG_CLICKS_TASK_QUEUE_NAME = "tap-news-log-clicks-task-queue"

PREFERENCE_MODEL_TABLE_NAME = "user_preference_model"
NEWS_TABLE_NAME = "news"

cloudAMQP_client = CloudAMQPClient(LOG_CLICKS_TASK_QUEUE_URL, LOG_CLICKS_TASK_QUEUE_NAME)

def handle_message(msg):
    if msg is None or not isinstance(msg, dict) :
        return

    if ('userId' not in msg
        or 'newsId' not in msg
        or 'timestamp' not in msg):
        return

    userId = msg['userId']
    newsId = msg['newsId']

    # Update user's preference
    db = mongodb_client.get_db()
    model = db[PREFERENCE_MODEL_TABLE_NAME].find_one({'userId': userId})

    # If model not exists, create a new one
    if model is None:
        print('Creating preference model for new user: %s' % userId)
        new_model = {'userId' : userId}
        preference = {}
        for i in news_classes.classes:
            preference[i] = float(INITIAL_P)
        new_model['preference'] = preference
        model = new_model

    print('Updating preference model for new user: %s' % userId)

    # Update model using time decaying method
    news = db[NEWS_TABLE_NAME].find_one({'digest': newsId})
    if (news is None
        or 'class' not in news
        or news['class'] not in news_classes.classes):

        print('Skipping processing...')
        return

    click_class = news['class']

    # Update the clicked one.
    old_p = model['preference'][click_class]
    model['preference'][click_class] = float((1 - ALPHA) * old_p + ALPHA)

    # Update not clicked classes.
    for i, prob in model['preference'].items():
        if not i == click_class:
            model['preference'][i] = float((1 - ALPHA) * model['preference'][i])

    print(model)
    db[PREFERENCE_MODEL_TABLE_NAME].replace_one({'userId': userId}, model, upsert=True)

def run():
    while True:
        if cloudAMQP_client is not None:
            msg = cloudAMQP_client.getMessage()
            if msg is not None:
                # Parse and process the task
                try:
                    handle_message(msg)
                except Exception as e:
                    print(e)
                    pass
            # Remove this if this becomes a bottleneck.
            cloudAMQP_client.sleep(SLEEP_TIME_IN_SECONDS)

if __name__ ==  "__main__":
    run()
```

## Step 2. Recommendation service

Create `recommendation_service/news_classes.py`

```python
classes = [
    "World",
    "US",
    "Business",
    "Technology",
    "Entertainment",
    "Sports",
    "Health",
    "Crime",
]
```

Create `recommendation_service/click_log_processor_test.py`

```python
import click_log_processor
import os
import sys

from datetime import datetime

# import common package in parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

import mongodb_client

PREFERENCE_MODEL_TABLE_NAME = "user_preference_model"
NEWS_TABLE_NAME = "news"

NUM_OF_CLASSES = 8

# Start MongoDB before running following tests.
def test_basic():
    db = mongodb_client.get_db()
    db[PREFERENCE_MODEL_TABLE_NAME].delete_many({"userId": "test_user"})

    msg = {"userId": "test_user",
           "newsId": "test_news",
           "timestamp": str(datetime.utcnow())}

    click_log_processor.handle_message(msg)

    model = db[PREFERENCE_MODEL_TABLE_NAME].find_one({'userId':'test_user'})
    assert model is not None
    assert len(model['preference']) == NUM_OF_CLASSES

    print('test_basic passed!')


if __name__ == "__main__":
    test_basic()
```

Test our `click_log_processor`

```
python3 click_log_processor_test.py
```

We don't want to expose the model database to external users. Therefore, we need an API to serve the preference model.

```python
import operator
import os
import sys

from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer

# import common package in parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

import mongodb_client

PREFERENCE_MODEL_TABLE_NAME = "user_preference_model"

SERVER_HOST = 'localhost'
SERVER_PORT = 5050

# compare floats for almost-equality in python
# https://stackoverflow.com/a/33024979
# https://www.python.org/dev/peps/pep-0485/#proposed-implementation
def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def getPreferenceForUser(user_id):
    """ Get user's preference in an ordered class list """
    db = mongodb_client.get_db()
    model = db[PREFERENCE_MODEL_TABLE_NAME].find_one({'userId':user_id})
    if model is None:
        return []

    sorted_tuples = sorted(list(model['preference'].items()), key=operator.itemgetter(1), reverse=True)
    sorted_list = [x[0] for x in sorted_tuples]
    sorted_value_list = [x[1] for x in sorted_tuples]

    # If the first preference is same as the last one, the preference makes
    # no sense.
    if isclose(float(sorted_value_list[0]), float(sorted_value_list[-1])):
        return []

    return sorted_list


# Threading HTTP Server
RPC_SERVER = SimpleJSONRPCServer((SERVER_HOST, SERVER_PORT))
RPC_SERVER.register_function(getPreferenceForUser, 'getPreferenceForUser')

print("Starting HTTP server on %s:%d" % (SERVER_HOST, SERVER_PORT))

RPC_SERVER.serve_forever()
```

Then we provide a client in `common` to let external users call the server.

Create `common/news_recommendation_service_client.py`

```python
import jsonrpclib

URL = "http://localhost:5050/"

client = jsonrpclib.ServerProxy(URL)

def getPreferenceForUser(userId):
    preference = client.getPreferenceForUser(userId)
    print("Preference list: %s" % str(preference))
    return preference
```

Create `common/news_recommendation_service_client_test.py`

```python
import news_recommendation_service_client as client

def test_basic():
	preference_list = client.getPreferenceForUser('test_user')
	assert len(preference_list) == 8
	print('test_basic passed.')

if __name__ == "__main__":
	test_basic()
```

## Step 3. Backend server

Update `backend_server/oprations.py`

```python
import news_recommendation_service_client
...
    # Get preference for the user
    # TODO: use perference to customize returned news list
    preference = news_recommendation_service_client.getPreferenceForUser(user_id)
    topPreference = None

    if preference is not None and len(preference) > 0:
        topPreference = preference[0]

    for news in sliced_news:
        # Remove text field to save bandwidth.
        del news['text']
        if 'class' in news and news['class'] == topPreference:
            news['reason'] = 'Recommend'
        if news['publishedAt'].date() == datetime.today().date():
            news['time'] = 'today'
    return json.loads(dumps(sliced_news))
    
```

Update `backend_server/operations_test.py`

```python
import operations
import os
import sys

# import common package in parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

from cloudAMQP_client import CloudAMQPClient

LOG_CLICKS_TASK_QUEUE_URL = "amqp://njghtiov:KMxNWfvqe_QxEiaFk26wnKytR2miTKoq@wombat.rmq.cloudamqp.com/njghtiov"
LOG_CLICKS_TASK_QUEUE_NAME = "tap-news-log-clicks-task-queue"


def test_getOneNews_basic():
    news = operations.getOneNews()
    assert news is not None
    print("test_getOneNews_basic passed!")

def test_getNewsSummariesForUser_basic():
    news = operations.getNewsSummariesForUser('test', 1)
    print(news)
    assert len(news) > 0
    print('test_getNewsSummariesForUser_basic passed!')

def test_getNewsSummariesForUser_invalid_pageNum():
    news = operations.getNewsSummariesForUser('test_user@gmail.com', -1)
    assert len(news) == 0
    print('test_getNewsSummariesForUser_invalid_pageNum passed!')

def test_getNewsSummariesForUser_large_pageNum():
    news = operations.getNewsSummariesForUser('test_user@gmail.com', 1000)
    assert len(news) == 0
    print('test_getNewsSummariesForUser_large_pageNum passed!')

def test_getNewsSummariesForUser_pagination():
    news_page_1 = operations.getNewsSummariesForUser('test', 1)
    news_page_2 = operations.getNewsSummariesForUser('test', 2)

    assert len(news_page_1) > 0
    assert len(news_page_2) > 0 

    digests_page_1_set = set(news['digest'] for news in news_page_1)
    digests_page_2_set = set(news['digest'] for news in news_page_2)

    assert len(digests_page_1_set.intersection(digests_page_2_set)) == 0

    print('test_getNewsSummariesForUser_pagination passed!')
    
def test_logNewsClickForUser():
    cloudAMQP_client = CloudAMQPClient(LOG_CLICKS_TASK_QUEUE_URL, LOG_CLICKS_TASK_QUEUE_NAME)
    operations.log_news_click_for_user('test_user', 'test_news')
    cloudAMQP_client.sleep(3)
    receivedMsg = cloudAMQP_client.getMessage()
    assert receivedMsg['userId'] == 'test_user'
    assert receivedMsg['newsId'] == 'test_news'
    print('test_logNewsClickForUser passed!')


if __name__ == "__main__":
    test_getOneNews_basic()
    test_getNewsSummariesForUser_basic()
    test_getNewsSummariesForUser_invalid_pageNum()
    test_getNewsSummariesForUser_large_pageNum()
    test_getNewsSummariesForUser_pagination()
    test_logNewsClickForUser()
    
```