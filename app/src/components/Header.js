import React, { useState, useEffect } from 'react';
import Navbar from 'react-bootstrap/Navbar';
import Button from 'react-bootstrap/Button';

function Header() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetch('/api/user')
      .then(response => response.json())
      .then(data => {
        if(!data.error) {
          setUser(data);
        }
      });
  }, []);

  function handleLogin() {
    window.location.href = "http://localhost:5000/login";
  }

  return (
    <Navbar bg="dark" variant="dark">
      <Navbar.Brand href="#home">OmniCalendar</Navbar.Brand>
      <Navbar.Collapse className="justify-content-end">
        {user ? <Navbar.Text>Welcome, {user.first_name}</Navbar.Text> : <Button variant="outline-success" onClick={handleLogin}>Login with Google</Button>}
      </Navbar.Collapse>
    </Navbar>
  );
}

export default Header;