import React from 'react';
import { Link } from 'react-router-dom'; // Add this line

function Sidebar() {
  return (
    <div className="sidebar">
      <h5></h5>
      <ul className="nav flex-column">
        <li className="nav-item">
          <Link className="nav-link" to="/">Link to Github</Link> 
        </li>
        <li className="nav-item">
          <Link className="nav-link" to="/add-calendar">Contact Details</Link> 
        </li>
      </ul>
    </div>
  );
}

export default Sidebar;