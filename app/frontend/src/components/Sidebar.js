import React from 'react';
import { Link } from 'react-router-dom'; // Add this line

function Sidebar() {
  return (
    <div className="sidebar">
      <h5>Sidebar</h5>
      <ul className="nav flex-column">
        <li className="nav-item">
          <Link className="nav-link" to="/">Item 1</Link> 
        </li>
        <li className="nav-item">
          <Link className="nav-link" to="/add-calendar">Add A Calendar</Link> 
        </li>
      </ul>
    </div>
  );
}

export default Sidebar;