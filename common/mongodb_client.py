from pymongo import MongoClient

MONGO_DB_HOST = 'localhost'
MONGO_DB_PORT = 27017
DB_NAME = 'tap-news'

client = MongoClient(MONGO_DB_HOST, MONGO_DB_PORT)

# singleton
def get_db(db=DB_NAME):
	db = client[db]
	return db

