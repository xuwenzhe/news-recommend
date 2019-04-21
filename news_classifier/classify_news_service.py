import os
import sys
import keras
import pickle
import numpy as np
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
from keras.preprocessing.text import Tokenizer
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences

# import common package in parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

import news_classes


SERVER_HOST = 'localhost'
SERVER_PORT = 6060

MAX_SEQUENCE_LENGTH = 1000 # truncate the sequences to a maximum length of 1000
model = load_model('news_classifier_v1.h5')
# load fitted tokenizer
# https://stackoverflow.com/a/45737582
with open('tokenizer.pickle','rb') as handle:
    tokenizer = pickle.load(handle)

def predict_news_class(news_string):
    sequences = tokenizer.texts_to_sequences([news_string])
    data = pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH)
    predictions = model.predict(data)
    return news_classes.classes[np.argmax(predictions[0])]

# print(predict_news_class(news))

# Threading HTTP Server
RPC_SERVER = SimpleJSONRPCServer((SERVER_HOST, SERVER_PORT))
RPC_SERVER.register_function(predict_news_class, 'predict_news_class')

print("Starting HTTP server on %s:%d" % (SERVER_HOST, SERVER_PORT))

RPC_SERVER.serve_forever()
