# Part 2 - Node Server

## Step 1. Refactor `client`

Two servers are used when we develop the client side `create-react-app` and the server side `node server (API)`. One advantage of using a development server for `create-react-app` is that we don't need to restart the server to monitor every client changes. Any changes will automatically show in our browser without restart the app. However, one problem is `create-react-app` cannot send API requests to the `node server` due to cross-region.

When the development work is done, only one server, i.e. node server, is involved. Two tasks of this server are:

1. send well-built `create-react-app` to the user's browser at the user first visit.
2. respond to client side API request.

No cross-region problem anymore.

```
# change name from 'tap-news' to 'client'
mv tap-news client
mkdir web_server
mv client web_server
cd web_server
```

## Step 2. install `express`

`express generator` is a tool to quickly create an application skeleton. See more info at its [official page](https://expressjs.com/en/starter/generator.html)

```
# web_server
npm install express-generator -g
cd server
npm install
npm start
```

A welcome page (localhost:3000) from express shows up.

![](./build_guide_figs/express-welcome.png)

## Step 3. install `nodemon`

```
sudo npm install --unsafe-perm -g nodemon
```

change `package.json, "start": "nodemon ./bin/www"`

delete: `user.js`, `error.jade`, `index.jade`, `layout.jade`

## Step 4. build client

```
# client
npm run build
```

## Step 5. update `app.js`

```javascript
// app.js
var express = require('express');
var path = require('path');

var indexRouter = require('./routes/index');

var app = express();

// view engine setup
app.set('views', path.join(__dirname, '../client/build'));
app.set('view engine', 'jade');
app.use('/static', express.static(path.join(__dirname, '../client/build/static')));

app.use('/', indexRouter);

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  res.status(404);
});

module.exports = app;
```

## Step 6. update `routes/index.js`

```javascript
// index.js node.js using ES5
var express = require('express');
var router = express.Router();
var path = require('path');


/* GET home page. */
router.get('/', function(req, res, next) {
  res.sendFile('index.html', { root: path.join(__dirname, '../../client/build') });
});

module.exports = router;
```

Note:

1. Look at [this reference](https://expressjs.com/en/api.html#res.sendFile) for more information about `sendFile`.

Now, at `server` folder, start node.js server to test whether the well-built react-app is sent to the visitor by `npm start`.

## Step 7. add `news.js`

```
touch server/routes/news.js
```

```javascript
// news.js RESTful API
var express = require('express');
var router = express.Router();

/* GET news list. */
router.get('/', function(req, res, next) {
  news = [
    {
      "source": "The Wall Street Journal",
      "title": "Berkshire",
      "description": "Berkshire posted a Berkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted a",
      "url": "https:",
      "utlToImage": "",
      "publishedAt": "2018-02-",
      "digest": "3Rju",
      "reason": "Recommend"
    },
    {
      "source": "The Wall Street Journal",
      "title": "Berkshire",
      "description": "Berkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted a",
      "url": "https:",
      "utlToImage": "",
      "publishedAt": "2018-02-",
      "digest": "3Rju",
      "reason": "Recommend"
    }
  ];
  res.json(news);
});

module.exports = router;
```

add newsRouter in `app.js`

```javascript
// var indexRouter = require('./routes/index');
var newsRouter = require('./routes/news');
// ...
// app.use('/', indexRouter);
app.use('/news', newsRouter);
```

Test newsRouter at `localhost:3000/news`

## Step 8. update `NewsPanel.js` in client side

```javascript
  loadMoreNews() {
    const news_url = 'http://' + window.location.hostname + ':3000' + '/news';
    const request = new Request(news_url, {method: 'GET'});
    fetch(request)
      .then(res => res.json())
      .then(news_list => {
        this.setState({
          news: this.state.news ? this.state.news.concat(news_list) : news_list,
        });
      })
  }
```

Notes:

1. fetch is an API provided by users' browser. Refer [this](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API) for more details.
2. `fetch` returns a promise. Use `then` to resolve. Transformation from string to json is another async promise. Use `then` to resolve.
3. concat fetched news with the existed news.

Rebuild again

```
# client
npm run build
```

Test node.js server

```
npm start
```

## Step 9. add `handleScroll`

```
# client
npm install --save lodash
```

```javascript
// NewsPanel.js
import _ from 'lodash';

  componentDidMount() {
    this.loadMoreNews();
    this.loadMoreNews = _.debounce(this.loadMoreNews, 1000);
    window.addEventListener('scroll', () => this.handleScroll());
  }
  handleScroll() {
    let scrollY = window.scrollY 
               || window.pageYOffset 
               || window.documentElement.scrollTop;
    if ( (window.innerHeight + scrollY) >= (document.body.offsetHeight - 50) ) {
      console.log('Loading more news...');
      this.loadMoreNews();
    }
  }
```

Note:

1. `lodash` is installed to debounce. Reduce the rate of API request rate triggered by users' scrolling.
2. `window.scrollY || window.pageYOffset || window.documentElement.scrollTop` here to consider all various browser namespaces.

Now rebuild `npm run build` (at client) and test `npm start` (at server)