# Part 8 - News Classifier

## Step 1. Train model ([GloVe](https://nlp.stanford.edu/projects/glove/), [20 Newsgroups](http://qwone.com/~jason/20Newsgroups/))

Train a news_classifier on colab. Save the model. A notebook training the model can be found [here](../news_classifier/tap_news_text_classifier.ipynb).

## Step 2. news classifier service

Create `news_classifier/classify_news_service.py`

```python
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

```

Create `common/classify_news_service_client.py`

```python
import jsonrpclib

URL = "http://localhost:6060/"

client = jsonrpclib.ServerProxy(URL)

def predict_news_class(news_string):
    news_class_string = client.predict_news_class(news_string)
    return news_class_string
```

Create `common/classify_news_service_client_test.py`

```python
import classify_news_service_client as client

def test_basic():
	news = "With strikeouts piling up, scoring plummeting, attendance falling and games often descending into all-or-nothing bores, it's no wonder that some people are calling for radical change to baseball. The sport faced a similar challenge 50 years ago, dogged by a scoring depression and lagging fan interest. In response, baseball's rules committee lowered the pitcher's mound 5 inches and tightened the strike zone, making it harder for pitchers to dominate the game. That sparked more scoring the next season — and more exciting games for fans."

	news_class_string = client.predict_news_class(news)
	print(news_class_string)
	assert news_class_string != ''
	print('test_basic passed.')

if __name__ == "__main__":
	test_basic()

```

Update `common/news_classes.py`

```python
classes = [
	'alt.atheism',
	'comp.graphics',
	'comp.os.ms-windows.misc',
	'comp.sys.ibm.pc.hardware',
	'comp.sys.mac.hardware',
	'comp.windows.x',
	'misc.forsale',
	'rec.autos',
	'rec.motorcycles',
	'rec.sport.baseball',
	'rec.sport.hockey',
	'sci.crypt',
	'sci.electronics',
	'sci.med',
	'sci.space',
	'soc.religion.christian',
	'talk.politics.guns',
	'talk.politics.mideast',
	'talk.politics.misc',
	'talk.religion.misc'
]
```


## Step 3. Call service when adding news to DB

Update `news_pipeline/news_deduper.py`

```python
...
import classify_news_service_client
...
    msg['class'] = classify_news_service_client.predict_news_class(msg['text'])
    print(msg['class'])
```