import React from "react";
import "./App.css";
import Navbar from "./components/Navbar.jsx";
import MainDashboard from "./components/MainDashboard.jsx";
import Sidebar from "./components/Sidebar.jsx";
import SyntheticPortfolios from "./components/SyntheticPortfolios.jsx"; // New import

export default function App() {
  return (
    <div className="app-container">
      <Navbar />
      {/* This body now controls the 3-column layout */}
      <div className="app-body">
        {/* Column 1: Left */}
        <SyntheticPortfolios />

        {/* Column 2: Middle */}
        <MainDashboard />

        {/* Column 3: Right */}
        <Sidebar />
      </div>
    </div>
  );
}

