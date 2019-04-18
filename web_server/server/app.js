// learn more about using expressJS at: https://youtu.be/L72fhGm1tfE


// import installed packages
var express = require('express');
var path = require('path');
var cors = require('cors');
var passport = require('passport');
var bodyParser = require('body-parser');


// import customized components
var config = require('./config/config.json');
require('./models/main.js').connect(config.mongoDbUri);
var localSignupStrategy = require('./auth/signup_passport');
var localLoginStrategy = require('./auth/login_passport');


var app = express();
// added to address port3000 conflict when client + server both run
// can be deleted at production phase
app.use(cors()); 
app.use(passport.initialize());
app.use(bodyParser.json());
passport.use('local-signup', localSignupStrategy);
passport.use('local-login', localLoginStrategy);


// view engine setup
app.set('views', path.join(__dirname, '../client/build/'));
app.set('view engine', 'jade');
app.use('/static', express.static(path.join(__dirname, '../client/build/static')));

// router or middleware
var indexRouter = require('./routes/index');
var authCheckMiddleware = require('./auth/auth_checker');
var newsRouter = require('./routes/news');
var auth = require('./routes/auth');
app.use('/', indexRouter);
app.use('/auth', auth);
app.use('/news', authCheckMiddleware); // always before other newsAPI
app.use('/news', newsRouter);


// catch 404 and forward to error handler
app.use(function(req, res, next) {
  res.status(404);
});

// https://stackoverflow.com/a/30205331
module.exports = app;
