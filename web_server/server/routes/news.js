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