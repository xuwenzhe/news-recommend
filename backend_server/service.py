""" backend service """
import logging
import os
import sys
import json
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
    res = mongodb_client.get_db()['news'].find_one()
    return json.loads(dumps(res))


SERVER = SimpleJSONRPCServer((SERVER_HOST, SERVER_PORT))
SERVER.register_function(add, 'add')
SERVER.register_function(get_one_news, 'getOneNews')

LOGGER.info('Starting RPC server on %s:%d', SERVER_HOST, SERVER_PORT)
SERVER.serve_forever()
