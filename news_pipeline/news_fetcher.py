import os
import sys

from newspaper import Article

# import common package in parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'scrapers'))

from cloudAMQP_client import CloudAMQPClient
import cnn_news_scraper

DEDUPE_NEWS_TASK_QUEUE_URL = "amqp://axfuxysf:v8X871ClpaBmFlor1T4rTwVSBMfj7GUI@wombat.rmq.cloudamqp.com/axfuxysf"
DEDUPE_NEWS_TASK_QUEUE_NAME = "tap-news-dedupe-news-task-queue"
SCRAPE_NEWS_TASK_QUEUE_URL = "amqp://xkbzolzd:4C-hGDUATyebdpj6JR_zrlJu7UHLja0r@wombat.rmq.cloudamqp.com/xkbzolzd"
SCRAPE_NEWS_TASK_QUEUE_NAME = "tap-news-scrape-news-task-queue"

SLEEP_TIME_IN_SECONDS = 5

dedupe_news_queue_client = CloudAMQPClient(DEDUPE_NEWS_TASK_QUEUE_URL, DEDUPE_NEWS_TASK_QUEUE_NAME)
scrape_news_queue_client = CloudAMQPClient(SCRAPE_NEWS_TASK_QUEUE_URL, SCRAPE_NEWS_TASK_QUEUE_NAME)


def handle_message(msg):
    if msg is None or not isinstance(msg, dict):
        print('message is broken')
        return

    text = None

    article = Article(msg['url'])
    article.download()
    article.parse()
    msg['text'] = article.text

    # if msg['source'] == 'cnn':
    #     text = cnn_news_scraper.extract_news(msg['url'])
    # msg['text'] = text
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

