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