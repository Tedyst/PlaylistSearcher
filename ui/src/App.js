import React, { useState, useEffect } from 'react';
import './App.css';
import Login from './views/Login';
import PlaylistView from './views/PlaylistView';
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
  Redirect
} from "react-router-dom";

let authenticated = true;

function requireAuth(nextState, replace, next) {
  if (!authenticated) {
    replace({
      pathname: "/auth",
      state: {nextPathname: nextState.location.pathname}
    });
  }
  console.log(nextState);
  next();
}

function App() {
  const [Logged, setLogged] = useState(true);
  fetch('/playlists').then(res => res.json()).then(data => {
      authenticated = data.logged;
      console.log(authenticated);
      setLogged(data.logged);
    });
  if(!authenticated){
    return (
      <Router>
        <Switch>
          <Route path="/auth">
            <Login />
          </Route>
          <Route path="/test" onEnter={requireAuth}>
            <Home />
          </Route>
          <Route path="/" onEnter={requireAuth}>
            <PlaylistView />
          </Route>
        </Switch>
        <Redirect to="/auth" />
      </Router>
    );
  }
  return (
    <Router>
      <Switch>
        <Route path="/auth">
          <Login />
        </Route>
        <Route path="/test" onEnter={requireAuth}>
          <Home />
        </Route>
        <Route path="/" onEnter={requireAuth}>
          <PlaylistView />
        </Route>
      </Switch>
    </Router>
  );
}

function Home() {
  return "Sal"
}

export default App;
