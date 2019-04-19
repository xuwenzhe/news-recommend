import datetime
import hashlib
import redis
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

import news_api_client
from cloudAMQP_client import CloudAMQPClient

SLEEP_TIME_IN_SECONDS = 60
NEWS_TIME_OUT_IN_SECONDS = 3600 * 24 * 3 # redis-check window

REDIS_HOST = 'localhost'
REDIS_PORT = 6379

SCRAPE_NEWS_TASK_QUEUE_URL = "amqp://xkbzolzd:4C-hGDUATyebdpj6JR_zrlJu7UHLja0r@wombat.rmq.cloudamqp.com/xkbzolzd"
SCRAPE_NEWS_TASK_QUEUE_NAME = "tap-news-scrape-news-task-queue"

NEWS_SOURCES = [
    'cnn'
]

redis_client = redis.StrictRedis(REDIS_HOST, REDIS_PORT)
cloudAMQP_client = CloudAMQPClient(SCRAPE_NEWS_TASK_QUEUE_URL, SCRAPE_NEWS_TASK_QUEUE_NAME)

while True:
    news_list = news_api_client.getNewsFromSource(NEWS_SOURCES)

    num_of_news_news = 0

    for news in news_list:
        # compare hash value instead of string to save time and space
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
