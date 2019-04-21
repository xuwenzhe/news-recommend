import classify_news_service_client as client

def test_basic():
	news = "With strikeouts piling up, scoring plummeting, attendance falling and games often descending into all-or-nothing bores, it's no wonder that some people are calling for radical change to baseball. The sport faced a similar challenge 50 years ago, dogged by a scoring depression and lagging fan interest. In response, baseball's rules committee lowered the pitcher's mound 5 inches and tightened the strike zone, making it harder for pitchers to dominate the game. That sparked more scoring the next season — and more exciting games for fans."

	news_class_string = client.predict_news_class(news)
	print(news_class_string)
	assert news_class_string != ''
	print('test_basic passed.')

if __name__ == "__main__":
	test_basic()