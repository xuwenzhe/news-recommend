import news_api_client as client

def test_basic():
    news = client.getNewsFromSource()
    assert len(news) > 0
    news = client.getNewsFromSource(sources=['ign'], sortBy='top')
    assert len(news) > 0
    print(news)
    print('test_basic passed!')

if __name__ == "__main__":
    test_basic()