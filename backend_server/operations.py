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
import news_recommendation_service_client
from cloudAMQP_client import CloudAMQPClient

LOG_CLICKS_TASK_QUEUE_URL = "amqp://njghtiov:KMxNWfvqe_QxEiaFk26wnKytR2miTKoq@wombat.rmq.cloudamqp.com/njghtiov"
LOG_CLICKS_TASK_QUEUE_NAME = "tap-news-log-clicks-task-queue"

cloudAMQP_client = CloudAMQPClient(LOG_CLICKS_TASK_QUEUE_URL, LOG_CLICKS_TASK_QUEUE_NAME)

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
    if page_num < 0:
        return []
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

def log_news_click_for_user(user_id, news_id):
    message = {'userId': user_id, 'newsId': news_id, 'timestamp': str(datetime.utcnow())}
    cloudAMQP_client.sendMessage(message)


