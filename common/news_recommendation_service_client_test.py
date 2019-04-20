import news_recommendation_service_client as client

def test_basic():
	preference_list = client.getPreferenceForUser('test_user')
	assert len(preference_list) == 8
	print('test_basic passed.')

if __name__ == "__main__":
	test_basic()