import datetime
import os
import sys

from dateutil import parser
from sklearn.feature_extraction.text import TfidfVectorizer

# import common package in parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

import mongodb_client
from cloudAMQP_client import CloudAMQPClient
import classify_news_service_client

DEDUPE_NEWS_TASK_QUEUE_URL = "amqp://axfuxysf:v8X871ClpaBmFlor1T4rTwVSBMfj7GUI@wombat.rmq.cloudamqp.com/axfuxysf"
DEDUPE_NEWS_TASK_QUEUE_NAME = "tap-news-dedupe-news-task-queue"

SLEEP_TIME_IN_SECONDS = 1

NEWS_TABLE_NAME = "news"

SAME_NEWS_SIMILARITY_THRESHOLD = 0.9

cloudAMQP_client = CloudAMQPClient(DEDUPE_NEWS_TASK_QUEUE_URL, DEDUPE_NEWS_TASK_QUEUE_NAME)

def handle_message(msg):
    if msg is None or not isinstance(msg, dict) :
        return
    text = msg['text']
    if text is None:
        return

    # get all recent news based on publishedAt
    published_at = parser.parse(msg['publishedAt'])
    published_at_day_begin = published_at - datetime.timedelta(days=1)
    published_at_day_end = published_at + datetime.timedelta(days=1)

    db = mongodb_client.get_db()
    same_day_news_list = list(db[NEWS_TABLE_NAME].find({'publishedAt': {'$gte': published_at_day_begin, '$lt': published_at_day_end}}))

    if same_day_news_list is not None and len(same_day_news_list) > 0:
        documents = [news['text'] for news in same_day_news_list]
        documents.insert(0, text)

        # Calculate similarity matrix
        tfidf = TfidfVectorizer().fit_transform(documents)
        pairwise_sim = tfidf * tfidf.T

        # print(pairwise_sim)

        rows, _ = pairwise_sim.shape

        for row in range(1, rows):
            if pairwise_sim[row, 0] > SAME_NEWS_SIMILARITY_THRESHOLD:
                # Duplicated news. Ignore.
                print("Duplicated news. Ignore.")
                return
    msg['publishedAt'] = parser.parse(msg['publishedAt'])
    # request classify_news_service_client for news_class
    msg['class'] = classify_news_service_client.predict_news_class(msg['text'])
    print(msg['class'])
    # http://api.mongodb.com/python/current/api/pymongo/collection.html
    replace_one_result = db[NEWS_TABLE_NAME].replace_one({'digest': msg['digest']}, msg, upsert=True) # update and insert
    # print("Local mongoDB Modified Count: ", replace_one_result.modified_count)
    # https://stackoverflow.com/a/49674531
    count_result = db[NEWS_TABLE_NAME].count()
    print("Local mongoDB Total Count: ", count_result)

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

        cloudAMQP_client.sleep(SLEEP_TIME_IN_SECONDS)