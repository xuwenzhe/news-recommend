""" backend service """
import logging
import os
import sys
import json
import operations
from bson.json_util import dumps
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer

# import common package in parent dir
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

import mongodb_client # pylint: disable=import-error, wrong-import-position


SERVER_HOST = 'localhost'
SERVER_PORT = 4040

LOGGER_FORMAT = '%(asctime)s - %(message)s'
logging.basicConfig(format=LOGGER_FORMAT)
LOGGER = logging.getLogger('backend_service')
LOGGER.setLevel(logging.DEBUG)

def add(num1, num2):
    """Test Method"""
    LOGGER.debug('Add is called with %d and %d', num1, num2)
    return num1 + num2

def get_one_news():
    """ Test method to get one news. """
    print("get_one_news is called")
    return operations.getOneNews()

def get_news_summaries_for_user(user_id, page_num):
    print("get_news_summaries_for_user is called with %s and %s" %(user_id, page_num))
    return operations.getNewsSummariesForUser(user_id, page_num)

def log_news_click_for_user(user_id, news_id):
    print("log_news_click_for_user is called with %s and %s" %(user_id, news_id))
    return operations.log_news_click_for_user(user_id, news_id)

RPC_SERVER = SimpleJSONRPCServer((SERVER_HOST, SERVER_PORT))
RPC_SERVER.register_function(add, 'add')
RPC_SERVER.register_function(get_one_news, 'getOneNews')
RPC_SERVER.register_function(get_news_summaries_for_user, 'getNewsSummariesForUser')
RPC_SERVER.register_function(log_news_click_for_user, 'logNewsClickForUser')

LOGGER.info('Starting RPC server on %s:%d', SERVER_HOST, SERVER_PORT)
RPC_SERVER.serve_forever()
