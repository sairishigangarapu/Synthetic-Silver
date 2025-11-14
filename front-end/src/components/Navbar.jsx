import React from "react";
import "./Navbar.css"; // This file defines the classes we are now using

export default function Navbar({ user, onLogout }) {
  return (
    <nav className="navbar">
      <h1 className="logo">Synthetic Commodities</h1>
      <div className="nav-right">
        {/* Use the "nav-links" class */}
      <ul className="nav-links">
        <li>Home</li>
        <li>Portfolio</li>
        <li>Profile</li>
        <li>
          <button className="login-btn" onClick={onLogout}>
              Logout
          </button>
        </li>
      </ul>
      </div>
      
      
    </nav>
  );
}




