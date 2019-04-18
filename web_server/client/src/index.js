import React from 'react';
import ReactDOM from 'react-dom';
import * as serviceWorker from './serviceWorker';

import Base from './Base/Base';


ReactDOM.render(
  <Base />,
  document.getElementById('root')
);

serviceWorker.unregister();
