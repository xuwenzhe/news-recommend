# Part 3 - Authentication
Refer to [this](https://stackoverflow.com/questions/1968722/how-cookies-work) about how cookies work. Cookies are often used in multi-page application. In our project which is a single-page application, Json Web Token (JWT) method is used. JWT is often sent from the server and stored in users' browser under `localStorage` under domain name.

We never want to store PLAIN password! Hash functions like SHA1 and MD5 are not safe. Known issues are rainbow table attack and password collision. A rainbow table is a precomputed table for reversing cryptographic hash functions, usually for cracking password hashes.

For each user, we generate a random a salt and add it to user's password. `f(password, salt) = hash(password + salt) <= stored hash`. 

## Step 1. Login Page
We split entire Login component to LoginForm and LoginPage. LoginForm focuses on rendering UI and LoginPage is responsible for handling logic.

Event handlers are passed from LoginPage to LoginForm.

Create `web_server/client/src/Login/LoginForm.js`

```javascript
import React from 'react';
import './LoginForm.css';

const LoginForm = ({
  onSubmit, // callback as arg
  onChange, // callback as arg
  errors    // errors obj
}) => (
  <div className="container">
    <div className="card-panel login-panel">
      <form className="col s12" action="/" onSubmit={onSubmit}>
        <h4 className="center-align">Login</h4>
        {errors.summary && <div className="row"><p className="error-message">{errors.summary}</p></div>}
        <div className="row">
          <div className="input-field col s12">
            <input className="validate" id="email" type="email" name="email" onChange={onChange}/>
            <label htmlFor='email'>Email</label>
          </div>
        </div>
        {errors.email && <div className="row"><p className="error-message">{errors.email}</p></div>}
        <div className="row">
          <div className="input-field col s12">
            <input className="validate" id="password" type="password" name="password" onChange={onChange}/>
            <label htmlFor='password'>Password</label>
          </div>
        </div>
        {errors.password && <div className="row"><p className="error-message">{errors.password}</p></div>}
        <div className="row right-align">
          <input type="submit" className="waves-effect waves-light btn indigo lighten-1" value='Log in'/>
        </div>
        <div className="row">
          <p className="right-align"> New to Tap News?  <a href="/signup">Sign Up</a></p>
        </div>
      </form>
    </div>
  </div>
);


export default LoginForm;
```

Create `web_server/client/src/Login/LoginForm.css`

```css
.login-panel {
  margin: auto;
  width: 40%;
}

.error-message {
  padding-left: 20px;
  color: red;
}
```

Create `web_server/client/src/Login/LoginPage.js`

```javascript
import React from 'react';
import LoginForm from './LoginForm';
import Auth from '../Auth/Auth';

class LoginPage extends React.Component {
  constructor(props) {
    super(props);

    // set the initial component state
    this.state = {
      errors: {},
      user: {
        email: '',
        password: ''
      }
    };
  }

  processForm(event) {
    event.preventDefault();

    const email = this.state.user.email;
    const password = this.state.user.password;

    console.log('email:', email);
    console.log('password:', password);

    // Post login data
  }

  changeUser(event) {
    const field = event.target.name;
    const user = this.state.user;
    user[field] = event.target.value;

    this.setState({user});
  }

  render() {
    return (
        <LoginForm
         onSubmit={(e) => this.processForm(e)} // provides callback
         onChange={(e) => this.changeUser(e)} // provides callback
         errors={this.state.errors}
         />
    );
  }
}

export default LoginPage;
```

Update `web_server/client/src/index.js` to see login page:

```javascript
// web_server/client/src/index.js
...
import LoginPage from './Login/LoginPage';
...
ReactDOM.render(<LoginPage />, document.getElementById('root'));
```

This following Login Error page should show up.

![](./build_guide_figs/login-page.png)

## Step 2. SignUp Page
We will do similar work for SignUp page.

Create `web_server/client/src/SignUp/SignUpForm.js`

```javascript
import React from 'react';
import './SignUpForm.css';

const SignUpForm = ({
  onSubmit,
  onChange,
  errors
}) => (
  <div className="container">
    <div className="card-panel signup-panel">
      <form className="col s12" action="/" onSubmit={onSubmit}>
        <h4 className="center-align">Sign Up</h4>
        {errors.summary && <div className="row"><p className="error-message">{errors.summary}</p></div>}
        <div className="row">
          <div className="input-field col s12">
            <input id="email" type="email" name="email" className="validate" onChange={onChange}/>
            <label htmlFor="email">Email</label>
          </div>
        </div>
        {errors.email && <div className="row"><p className="error-message">{errors.email}</p></div>}
        <div className="row">
          <div className="input-field col s12">
            <input id="password" type="password" name="password" className="validate" onChange={onChange}/>
            <label htmlFor="password">Password</label>
          </div>
        </div>
        {errors.password && <div className="row"><p className="error-message">{errors.password}</p></div>}
        <div className="row">
          <div className="input-field col s12">
            <input id="confirm_password" type="password" name="confirm_password" className="validate" onChange={onChange}/>
            <label htmlFor="confirm_password">Confirm Password</label>
          </div>
        </div>
        <div className="row right-align">
          <input type="submit" className="waves-effect waves-light btn indigo lighten-1" value='Sign Up'/>
        </div>
        <div className="row">
          <p className="right-align"> Already have an account? <a href="/login">Login</a></p>
        </div>
      </form>
    </div>
  </div>
);


export default SignUpForm;
```
Create `web_server/client/src/SignUp/SignUpForm.css`

```css
.signup-panel {
  margin: auto;
  width: 40%;
}

.error-message {
  padding-left: 20px;
  color: red;
}
```

Create `web_server/client/src/SignUp/SignUpPage.js`

```javascript
import React from 'react';
import SignUpForm from './SignUpForm';

class SignUpPage extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      errors: {},
      user: {
        email: '',
        password: '',
        confirm_password: ''
      }
    };
  }

  processForm(event) {
    event.preventDefault();

    const email = this.state.user.email;
    const password = this.state.user.password;
    const confirm_password = this.state.user.confirm_password;

    console.log('email:', email);
    console.log('password:', password);
    console.log('confirm_password:', confirm_password);

    if (password !== confirm_password) {
      return;
    }

    // Post signup data
  }

  changeUser(event) {
    const field = event.target.name;
    const user = this.state.user;
    user[field] = event.target.value;

    this.setState({user});

    const errors = this.state.errors;
    if (this.state.user.password !== this.state.user.confirm_password) {
      errors.password = "Password and Confirm Password don't match.";
    } 
    else {
      errors.password = '';
    }
    this.setState({errors});
  }

  render() {
    return (
      <SignUpForm
        onSubmit={(e) => this.processForm(e)}
        onChange={(e) => this.changeUser(e)}
        errors={this.state.errors}
      />
    );
  }
}

export default SignUpPage;
```

Update `web_server/client/src/index.js`, we can see our SignUp Page.

```javascript
...
import SignUpPage from './SignUp/SignUpPage';
...
ReactDOM.render(<SignUpPage />, document.getElementById('root'));
```

![](./build_guide_figs/signup-page.png)

## Step 3. Authentication
#### Local Storage
We need a new module to handle authentication. To be more specific, we are going to use LocalStorage to store the state of authentication. LocalStorage is introduced in HTML. With local storage, web applications can store data locally within the user's browser.

Before HTML5, application data had to be stored in cookies, included in every server request. Local storage is more secure, and large amounts of data can be stored locally, without affecting website performance.

Unlike cookies, the storage limit is far larger (at least 5MB) and information is never transferred to the server.

Local storage is per origin (per domain and protocol). All pages, from one origin, can store and access the same data.

While on the subject, if you want to support most browsers, then do not exceed 50 cookies per domain, and 4093 bytes per domain. That is the size of all cookies should not exceed 4093 bytes. This means you can have 1 cookie of 4093 bytes, or 2 cookies of 2045 bytes, etc.

Create `web_server/client/src/Auth/Auth.js`

```javascript
// Component 'Auth' provides manipulation operations 
// to user's token in Browser's localStorage

class Auth {
  static authenticateUser(token, email) {
    localStorage.setItem('token', token);
    localStorage.setItem('email', email);
  }

  static isUserAuthenticated() {
    return localStorage.getItem('token') !== null;
  }

  static deauthenticateUser() {
    localStorage.removeItem('token');
    localStorage.removeItem('email');
  }

  static getToken() {
    return localStorage.getItem('token');
  }

  static getEmail() {
    return localStorage.getItem('email');
  }
  
}

export default Auth;
```

## Step 4. add component Base
Now we are going to add a navigation bar in our App. The navBar includes 'login', 'register' or 'logout' if logged in.

To add the navBar, we will wrap our app in a new component - Base component.

Create `web_server/client/src/Base/Base.js`

```javascript
import 'materialize-css/dist/css/materialize.min.css';
import 'materialize-css/dist/js/materialize.js';

import React from 'react';
import { BrowserRouter as Router, Route, Link } from 'react-router-dom';

import Auth from '../Auth/Auth';
import LoginPage from '../Login/LoginPage';
import SignUpPage from '../SignUp/SignUpPage';
import App from '../App/App';
import './Base.css';


const logout = () => {
  Auth.deauthenticateUser();
  window.location.replace('/');
};

// WRONG: /auth/login or /auth/signup
// use react routing not express routing here
// Quickstart about react-router-dom V5
// https://reacttraining.com/react-router/web/guides/quick-start
const Base = () => (
  <Router>
    <div>
      <nav className="nav-bar indigo lighten-1">
        <div className="nav-wrapper">
          <a href="/" className="brand-logo">  Tap News</a>
          <ul id="nav-mobile" className="right">
            {Auth.isUserAuthenticated() ?
              (<div>
                 <li>{Auth.getEmail()}</li>
                 <li><a onClick={logout}>Log out</a></li>
               </div>)
               :
              (<div>
                 <li><Link to="/login">Log in</Link></li>
                 <li><Link to="/signup">Sign up</Link></li>
               </div>)
            }
          </ul>
        </div>
      </nav>
      <br/>
      <Route exact path="/" render={() => (Auth.isUserAuthenticated() ? (<App />) : (<LoginPage />))}/>
      <Route exact path="/login" component={LoginPage} />
      <Route exact path="/signup" component={SignUpPage} />
    </div>
  </Router>
);

export default Base;
```

Create `web_server/client/src/Base/Base.css`

```css
/*Base.css*/
.nav-wrapper {
  background-color: transparent;
}
```

## Step 5. Change to React Link

Update `web_server/client/src/Login/LoginForm.js` and `web_server/client/src/SignUp/SignUpForm.js`

```
import { Link } from 'react-router-dom'
...
<Link to="/signup">Log in</Link>
```

## Step 6. Add data post in LoginPage
Update `web_server/client/src/Login/LoginPage.js`

```javascript
    // Post login data
    // refer to authAPI web_server/server/routes/auth.js
    // compare APIcall(express) VS. pageViewReq(react):
    // https://stackoverflow.com/a/49310656
    // learn more about react client-side routing:
    // https://stackoverflow.com/a/36623117
    const url = 'http://' + window.location.hostname + ':3000' + '/auth/login';
    const request = new Request(// similar usage in Postman
      url,
      {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email: this.state.user.email,
          password: this.state.user.password
        })// no ';' here
      }
    );
    fetch(request).then(response => {
      if (response.status === 200) {
        console.log('test login react')
        this.setState({ errors: {} });
        response.json().then(json => {
          console.log(json);
          Auth.authenticateUser(json.token, email);
          // refer to ../Base/Base.js
          window.location.replace('/');
        });
      }
      else {
        console.log('Login failed');
        response.json().then(json => {
          const errors = json.errors ? json.errors : {};
          errors.summary = json.message;
          this.setState({errors});
        });
      }
    });
```

## Step 7. Add data post in SignUpPage
Update `web_server/client/src/SignUp/SignUpPage.js`

```javascript
    // Post signup data
    // refer to the authAPI at web_server/server/routes/auth.js
    // compare APIcall(express) VS. pageViewReq(react)
    // https://stackoverflow.com/a/49310656
    const url = 'http://' + window.location.hostname + ':3000' + '/auth/signup';
    const request = new Request( // similar usage in Postman
      url,
      {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email: this.state.user.email,
          password: this.state.user.password
        }) // no ';'
      }
    );
    fetch(request).then(response => {
      if (response.status === 200) {
        this.setState({errors: {}});
        window.location.replace('/');
      }
      else {
        response.json().then(json => {
          console.log(json);
          const errors = json.errors ? json.errors : {};
          errors.summary = json.message;
          console.log(this.state.errors);
          this.setState({errors});
        });
      }
    });
```

## Step 8. install `react-router-dom`

```
# client
npm install --save react-router-dom
```

Update `web_server/client/src/index.js` to adopt Base

```javascript
import React from 'react';
import ReactDOM from 'react-dom';
import * as serviceWorker from './serviceWorker';

import Base from './Base/Base';


ReactDOM.render(
  <Base />,
  document.getElementById('root')
);

serviceWorker.unregister();
```

## Step 9. install `cors`
To make development easier, we would like to run react and server on two development servers. Therefore, we need to solve COR issue.

```
# server
npm install --save cors
```

Update `web_server/server/app.js`

```javascript
var cors = require('cors');
// added to address port3000 conflict when client + server both run
// can be deleted at production phase
app.use(cors()); 
```

## Step 10. add `config.json`
Since we will have lots of configurations. It is better to have a single place for all configurations. 

Create `web_server/server/config/config.json`

```json
{
  "mongoDbUri": "mongodb+srv://test:test@news-recommend-9itft.mongodb.net/test?retryWrites=true",
  "jwtSecret": "a secret phrase!!"
}
```

## Step 11. integrate with Mongoose

We will use mongoose to handle user information.


```
# server
npm install --save mongoose
```

Create `web_server/server/models/user.js`

```javascript
const mongoose = require('mongoose');
const bcrypt = require('bcrypt');

const UserSchema = new mongoose.Schema({
  email: {
    type: String,
    index: {unique: true}
  },
  password: String  
});

// arrow function with 'this' is not safe here
UserSchema.methods.comparePassword = function comparePassword(password, callback) {
  bcrypt.compare(password, this.password, callback);
};
 
// necessary check before 'save' to the database
// arrow function with 'this' is not safe here
UserSchema.pre('save', function saveHook(next) { 
  const user = this;
  // proceed further only if the password is modified or the user is new
  if (!user.isModified('password')) return next();
  return bcrypt.genSalt((saltError, salt) => {
    if (saltError) {return next(saltError);}
    return bcrypt.hash(user.password, salt, (hashError, hash) => {
      if (hashError) {return next(hashError);}
      // replace a password string with hash value
      user.password = hash;
      return next();
    }); 
  });
});

module.exports = mongoose.model('User', UserSchema);
```

and `main.js` to configure mongoose models.

Create `web_server/server/models/main.js`

```javascript
// main.js provides a 'connect' function to easily access to mongoDB atlas
// learn nore about using mongoose at: https://youtu.be/WDrU305J1yw

const mongoose = require('mongoose');

module.exports.connect = uri => {
  mongoose.connect(uri);
  mongoose.connection.on('error', err => {
  	console.error(`Mongoose connection error: ${err}`);
  	process.exit(1);
  });
  // load models
  require('./user');
};
```

Update `web_server/server/app.js`

```javascript
var config = require('./config/config.json');
require('./models/main.js').connect(config.mongoDbUri);
```

## Step. 12 install `bcrypt`

```
# server
npm install --save bcrypt
```

## Step. 13 Passport and JWT

We use `passport` to handle login/signup. We also uses `jwt` to handle session.

```
npm install --save passport
npm install --save passport-local
npm install --save jsonwebtoken
```

Create `web_server/server/auth/login_passport.js`

```javascript
const jwt = require('jsonwebtoken');
const User = require('mongoose').model('User');
const PassportLocalStrategy = require('passport-local').Strategy;
const config = require('../config/config.json');

module.exports = new PassportLocalStrategy({
  usernameField: 'email',
  passwordField: 'password',
  session: false,
  passReqToCallback: true
}, (req, email, password, done) => {
  const userData = {
  	email: email.trim(),
  	password: password
  };
  // find a user by email address
  return User.findOne({email: userData.email}, (err, user) => {
  	if (err) {return done(err);}
  	if (!user) {
  	  const error = new Error('Incorrect email or password');
  	  error.name = 'IncorrectCredentialsError';
  	  return done(error);
  	}

  	// check if a hashed user's password is equal to a value saved in the database
  	return user.comparePassword(userData.password, (passwordErr, isMatch) => {
  	  if (err) {return done(err);}
  	  if (!isMatch) {
  	  	const error = new Error('Incorrect email or password');
  	  	error.name = 'IncorrectCredentialsError';
  	  	return done(error);
  	  }
  	  const payload = {sub: user._id};
  	  // create a token string
  	  const token = jwt.sign(payload, config.jwtSecret);
  	  const data = {name: user.email};
  	  return done(null, token, data);
  	});
  });
});
```

Create `web_server/server/auth/signup_passport.js`

```javascript
const User = require('mongoose').model('User');
const PassportLocalStrategy = require('passport-local').Strategy;

module.exports = new PassportLocalStrategy({
  usernameField: 'email',
  passwordField: 'password',
  passReqToCallback: true
}, (req, email, password, done) => {
  const userData = {
  	email: email.trim(),
  	password: password
  };
  const newUser = new User(userData);
  newUser.save((err) => {
  	console.log('Save new user!');
  	if (err) {return done(err)};
  	return done(null);
  });
});
```

For detailed usage documentation about passport-local ’s Strategy: refer to [this](https://github.com/jaredhanson/passport-local/blob/master/lib/strategy.js)
And [this](https://github.com/jaredhanson/passport) about passport.

Update passport's configuration in `web_server/server/app.js`

```javascript
var passport = require('passport');
app.use(passport.initialize());
var localSignupStrategy = require('./auth/signup_passport');
var localLoginStrategy = require('./auth/login_passport');
passport.use('local-signup', localSignupStrategy);
passport.use('local-login', localLoginStrategy);
```

## Step. 14 AuthChecker

For every incoming requests, we need to check if the user has logged in. If not, we redirects them to login page. To achieve this, we will build a middleware for auth check.

Create `web_server/server/auth/auth_checker.js`

```javascript
const jwt = require('jsonwebtoken');
const User = require('mongoose').model('User');
const config = require('../config/config.json');

// this middleware gets called everytime when request newsAPI
// refer to app.js for "router or middleware" section.
module.exports = (req, res, next) => {
  console.log('auth_checker: req: ' + req.headers);
  if (!req.headers.authorization) {return res.status(401).end();}
  // get the last part from an authorization header string like "bearer token-value"
  const token = req.headers.authorization.split(' ')[1];
  console.log('auth_checker: token: ' + token);
  // decode the token using a secret key-phrase
  return jwt.verify(token, config.jwtSecret, (err, decoded) => {
  	// the 401 code is for unauthorized status
  	if (err) {return res.status(401).end();}
  	const id = decoded.sub;
  	// check if a user exists
  	return User.findById(id, (userErr, user) => {
  	  if (userErr || !user) {return res.status(401).end();}
  	  return next(); // "middle"ware
  	});
  });
};
```

Don't forget to install it in `app.js` for all incoming `/news` requests.

Update `web_server/server/app.js`

```javascript
var authCheckMiddleware = require('./auth/auth_checker');
app.use('/news', authCheckMiddleware); // always before other newsAPI
```

## Step 15. Auth Request Handler

```
# server
npm install --save body-parser
```

Update `web_server/server/app.js`

```javascript
var bodyParser = require('body-parser');
app.use(bodyParser.json());
```

```
# server
npm install --save validator
```

Create `web_server/server/routes/auth.js`

```javascript
const express = require('express');
const passport = require('passport');
const router = express.Router();
const validator = require('validator');

router.post('/signup', (req, res, next) => {
  const validationResult = validateSignupForm(req.body);
  if (!validationResult.success) {
    console.log('validationResult failed');
    return res.status(400).json({
      success: false,
      message: validationResult.message,
      errors: validationResult.errors
    });
  }
  return passport.authenticate('local-signup', (err) => {
    if (err) {
      console.log(err);
      if (err.name === 'MongoError' && err.code === 11000) {
        // the 11000 Mongo code is for a duplication email error
        // the 409 HTTP status code is for conflict error
        return res.status(409).json({
          success: false,
          message: 'Check the form for errors.',
          errors: {email: 'This email is already taken.'}
        });
      }
      return res.status(400).json({
        success: false,
        message: 'Could not process the form.'
      });
    }
    return res.status(200).json({
      success: true,
      message: 'You have successfully signed up! Now you should be able to log in.'
    });
  })(req, res, next);
});

router.post('/login', (req, res, next) => {
  const validationResult = validateLoginForm(req.body);
  if (!validationResult.success) {
    return res.status(400).json({
      success: false,
      message: validationResult.message,
      errors: validationResult.errors
    });
  }
  return passport.authenticate('local-login', (err, token, userData) => {
    if (err) {
      if (err.name === 'IncorrectCredentialsError') {
        return res.status(400).json({
          success: false,
          message: err.message
        });
      }
      return res.status(400).json({
        success: false,
        message: 'Could not process the form: ' + err.message
      });
    }
    return res.json({
      success: true,
      message: 'You have successfully logged in!',
      token,
      user: userData
    });
  })(req, res, next);
});


function validateSignupForm(payload) {
  console.log(payload);
  const errors = {};
  let isFormValid = true;
  let message = '';

  if (!payload || typeof payload.email !== 'string' || !validator.isEmail(payload.email)) {
    isFormValid = false;
    errors.email = 'Please provide a correct email address.';
  }
  if (!payload || typeof payload.password !== 'string' || payload.password.length < 8) {
    isFormValid = false;
    errors.password = 'Password must have at least 8 characters.';
  }
  if (!isFormValid) {
    message = 'Check the form for errors.';
  }
  return {
    success: isFormValid,
    message,
    errors
  };
}


function validateLoginForm(payload) {
  console.log(payload);
  const errors = {};
  let isFormValid = true;
  let message = '';
  if (!payload || typeof payload.email !== 'string' || payload.email.trim().length === 0) {
    isFormValid = false;
    errors.email = 'Please provide your email address.';
  }
  if (!payload || typeof payload.password !== 'string' || payload.password.length === 0) {
    isFormValid = false;
    errors.password = 'Please provide your password.';
  }
  if (!isFormValid) {
    message = 'Check the form for errors.';
  }
  return {
    success: isFormValid,
    message,
    errors
  };
}

module.exports = router;
```

Now `npm start` both client and server to test signup and login functions!

Don't forget to add token in NewsPanel when using newsAPI

Update `web_server/client/src/NewsPanel/NewsPanel.js`

```javascript
import Auth from '../Auth/Auth';
  loadMoreNews() {
    // refer to newsAPI at web_server/server/routes/news.js
    const news_url = 'http://' + window.location.hostname + ':3000' + '/news';
    const request = new Request(news_url, {
      method: 'GET',
      headers: {
        'Authorization': 'bearer ' + Auth.getToken(),
      },
    });
```