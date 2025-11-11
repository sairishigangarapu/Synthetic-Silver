import React from "react";
import "./Navbar.css"; // This file defines the classes we are now using

export default function Navbar() {
  return (
    // Use the "navbar" class from Navbar.css
    <nav className="navbar">
      {/* Use the "logo" class */}
      <h1 className="logo">ETF Dashboard</h1>
      <div className="nav-centre">
        <input type="text" placeholder="Search assets..." className="search-bar" />
      </div>
      <div className="nav-right">
        {/* Use the "nav-links" class */}
      <ul className="nav-links">
        <li>Home</li>
        <li>Portfolio</li>
        <li>Profile</li>
        <li><button className="login-btn">Login</button></li>
      </ul>
      </div>
      
      
    </nav>
  );
}




