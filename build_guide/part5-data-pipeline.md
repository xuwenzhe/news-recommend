# Part 5 - Data Pipeline

## Step 1. News Monitor
Since `mongodb_client` and `cloudAMQP_client` are used not only in backend-service but also in data pipeline. Hence refractor these utility files into `common` directory.

Sign up [NewsAPI](https://newsapi.org/docs/get-started) to get an API key.

Install [`requests`](http://docs.python-requests.org/en/master/)

```
pip3 install requests
```

Since `NewsAPI` doesn't know what news we have received, we need redis to check whether newly fetched news are received before add them into our cloudAMQP (`tap-news-scrape-news-task-queue`).

Install [`redis`](https://redis.io/topics/quickstart) via `brew`

```
brew install redis
```

Start redis service

```
brew services start redis
brew services list
brew services stop redis
```

To flush data in redis, use

```
redis-cli flushall
```


https://stackoverflow.com/a/36136243


Create `news_pipeline/news_monitor.py`

```python
import datetime
import hashlib
import redis
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

import news_api_client
from cloudAMQP_client import CloudAMQPClient

SLEEP_TIME_IN_SECONDS = 10
NEWS_TIME_OUT_IN_SECONDS = 3600 * 24 * 3 # redis-check window

REDIS_HOST = 'localhost'
REDIS_PORT = 6379

SCRAPE_NEWS_TASK_QUEUE_URL = ""
SCRAPE_NEWS_TASK_QUEUE_NAME = "tap-news-scrape-news-task-queue"

NEWS_SOURCES = [
    'bbc-news',
    'bbc-sport',
    'bloomberg',
    'cnn',
    'entertainment-weekly',
    'espn',
    'ign',
    'techcrunch',
    'the-new-york-times',
    'the-wall-street-journal',
    'the-washington-post'
]

redis_client = redis.StrictRedis(REDIS_HOST, REDIS_PORT)
cloudAMQP_client = CloudAMQPClient(SCRAPE_NEWS_TASK_QUEUE_URL, SCRAPE_NEWS_TASK_QUEUE_NAME)

while True:
    news_list = news_api_client.getNewsFromSource(NEWS_SOURCES)

    num_of_news_news = 0

    for news in news_list:
        # compare hash value instead of string to save time and space
        # https://stackoverflow.com/a/54624683
        news_digest = hashlib.md5(news['title'].encode('utf-8')).hexdigest()

        if redis_client.get(news_digest) is None:
            num_of_news_news += 1
            news['digest'] = news_digest

            if news['publishedAt'] is None:
                news['publishedAt'] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

            redis_client.set(news_digest, "True") # only care key not value here
            redis_client.expire(news_digest, NEWS_TIME_OUT_IN_SECONDS)

            cloudAMQP_client.sendMessage(news)

    print("Fetched %d news." % num_of_news_news)

    # sleep with AMQP heartbeat
    cloudAMQP_client.sleep(SLEEP_TIME_IN_SECONDS)
```

A `queue_helper` file is created to flush cloudAMQP

```python
import os
import sys

# import common package in parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

from cloudAMQP_client import CloudAMQPClient

DEDUPE_NEWS_TASK_QUEUE_URL = "amqp://mycayzfr:E4nnofIrEfvgW4oByDmkoBjvsmobCzFG@termite.rmq.cloudamqp.com/mycayzfr"
DEDUPE_NEWS_TASK_QUEUE_NAME = "top-new-DEDUPE_NEWS_TASK_QUEUE_NAME"
SCRAPE_NEWS_TASK_QUEUE_URL = ""
SCRAPE_NEWS_TASK_QUEUE_NAME = "tap-news-scrape-news-task-queue"

def clearQueue(queue_url, queue_name):
    scrape_news_queue_client = CloudAMQPClient(queue_url, queue_name)

    num_of_messages = 0

    while True:
        if scrape_news_queue_client is not None:
            msg = scrape_news_queue_client.getMessage()
            if msg is None:
                print("Cleared %d messages." % num_of_messages)
                return
            num_of_messages += 1


if __name__ == "__main__":
    clearQueue(SCRAPE_NEWS_TASK_QUEUE_URL, SCRAPE_NEWS_TASK_QUEUE_NAME)
    clearQueue(DEDUPE_NEWS_TASK_QUEUE_URL, DEDUPE_NEWS_TASK_QUEUE_NAME)
```

## Step 2. Scrapers
Install lxml

```
pip3 install lxml
```

Use `xpath helper`, a Chrome extension, to search `xpath` for articles.

```
GET_CNN_NEWS_XPATH = """//p[contains(@class, 'zn-body__paragraph')]//text() | //div[contains(@class, 'zn-body__paragraph')]//text()"""
```

Create `news_pipeline/scrapers/cnn_news_scraper.py`

```python
import os
import random
import requests

from lxml import html

GET_CNN_NEWS_XPATH = """//p[contains(@class, 'zn-body__paragraph')]//text() | //div[contains(@class, 'zn-body__paragraph')]//text()"""

# Load user agents to avoid scraper-forbidden
USER_AGENTS_FILE = os.path.join(os.path.dirname(__file__), 'user_agents.txt')
USER_AGENTS = []

with open(USER_AGENTS_FILE, 'rb') as uaf:
    for ua in uaf.readlines():
        if ua:
            USER_AGENTS.append(ua.strip()[1:-1]) # get rid of ""

random.shuffle(USER_AGENTS)


def _get_headers():
    ua = random.choice(USER_AGENTS)
    headers = {
      "Connection" : "close", 
      "User-Agent" : ua
    }
    return headers

def extract_news(news_url):
    session_requests = requests.session() # mimic browser to avoid scraper-forbidden
    response = session_requests.get(news_url, headers=_get_headers())
    news = {}

    try:
        tree = html.fromstring(response.content)
        news = tree.xpath(GET_CNN_NEWS_XPATH)
        news = ''.join(news)
    except Exception:
        return {}

    return news

```

Test this CNN scraper with a 2017 article

Create `news_pipeline/scrapers/cnn_news_scraper_test.py`

```python
import cnn_news_scraper as scraper

EXPECTED_NEWS = "Santiago is charged with using and carrying a firearm during and in relation to a crime of violence"
CNN_NEWS_URL = "http://edition.cnn.com/2017/01/17/us/fort-lauderdale-shooter-isis-claim/index.html"

def test_basic():
    news = scraper.extract_news(CNN_NEWS_URL)

    print(news)
    assert EXPECTED_NEWS in news
    print('test_basic passed!')

if __name__ == "__main__":
    test_basic()
```

## Step 3. News Fetcher

Create `news_pipeline/news_fetcher.py`

```python
import os
import sys

# import common package in parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'scrapers'))

from cloudAMQP_client import CloudAMQPClient
import cnn_news_scraper

DEDUPE_NEWS_TASK_QUEUE_URL = ""
DEDUPE_NEWS_TASK_QUEUE_NAME = "tap-news-dedupe-news-task-queue"
SCRAPE_NEWS_TASK_QUEUE_URL = ""
SCRAPE_NEWS_TASK_QUEUE_NAME = "tap-news-scrape-news-task-queue"

SLEEP_TIME_IN_SECONDS = 5

dedupe_news_queue_client = CloudAMQPClient(DEDUPE_NEWS_TASK_QUEUE_URL, DEDUPE_NEWS_TASK_QUEUE_NAME)
scrape_news_queue_client = CloudAMQPClient(SCRAPE_NEWS_TASK_QUEUE_URL, SCRAPE_NEWS_TASK_QUEUE_NAME)


def handle_message(msg):
    if msg is None or not isinstance(msg, dict):
        print('message is broken')
        return

    text = None

    if msg['source'] == 'cnn':
        text = cnn_news_scraper.extract_news(msg['url'])
    msg['text'] = text
    dedupe_news_queue_client.sendMessage(msg)

while True:
    if scrape_news_queue_client is not None:
        msg = scrape_news_queue_client.getMessage()
        if msg is not None:
            # Parse and process the task
            try:
                handle_message(msg)
            except Exception as e:
                print(e)
                pass
        dedupe_news_queue_client.sleep(SLEEP_TIME_IN_SECONDS)
```

## Step 4. News Deduper

Install `tf-idf` dependent packages

```
pip3 install python-dateutil sklearn numpy scipy
```

Test [`TfidfVectorizer`](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html) from `sklearn`.

Create `news_pipeline/tf_idf_deduper_test_1.py`

```python
from sklearn.feature_extraction.text import TfidfVectorizer

doc1 = "I like apples. I like oranges too"
doc2 = "I like apples. I like doctors"
doc3 = "An apple a day keeps the doctor away"
doc4 = "Never compare an apple to an orang"

documents = [doc1, doc2, doc3, doc4]

tfidf = TfidfVectorizer().fit_transform(documents)
pairwise_sim = tfidf * tfidf.T

# https://stackoverflow.com/a/27220066
print(pairwise_sim.A)
```

Create `news_pipeline/tf_idf_deduper_test_2.py`.

Create a helper script `news_pipeline/news_pipeline_launcher.sh` to launch monitor, fetcher, and deduper together.

```bash
python3 news_monitor.py &
python3 news_fetcher.py &
python3 news_deduper.py &

echo "=================================================="
read -p "PRESS [ENTER] TO TERMINATE PROCESSES." PRESSKEY

kill $(jobs -p)
```

Change it to executable file by

```
sudo chmod +x news_pipeline_launcher.sh
```

Enter to kill all pipeline processes. 

```
sudo killall Python
```

pip3 install tensorflow


## Step 5. `newspaper3k`
Instead of writing our own scrapers, we can use [`newspaper3k`](https://newspaper.readthedocs.io/en/latest/), a 3rd-party scraper package. This package focuses more on `generalization` than `accuracy` compared to our own scrapper.

Install `newspaper3k`

```
pip3 install newspaper3k
```

Update `news_pipeline/news_fetcher.py`

```python
from newspaper import Article
...
    article = Article(msg['url'])
    article.download()
    article.parse()
    msg['text'] = article.text
```

