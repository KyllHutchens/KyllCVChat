import React, { useState, useEffect } from 'react';
import Navbar from 'react-bootstrap/Navbar';
import Button from 'react-bootstrap/Button';

function Header() {

  return (
    <Navbar bg="dark" variant="dark">
      <Navbar.Brand href="/">   Kyll Hutchens CV Chat</Navbar.Brand>
      <Navbar.Collapse className="justify-content-end">
      </Navbar.Collapse>
    </Navbar>
  );
}

export default Header;