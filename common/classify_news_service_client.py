import jsonrpclib

URL = "http://localhost:6060/"

client = jsonrpclib.ServerProxy(URL)

def predict_news_class(news_string):
    news_class_string = client.predict_news_class(news_string)
    return news_class_string