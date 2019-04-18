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