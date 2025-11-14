import React from "react";
import "./App.css";
import Navbar from "./components/Navbar.jsx";
import MainDashboard from "./components/MainDashboard.jsx";
import Sidebar from "./components/Sidebar.jsx";
import SyntheticPortfolios from "./components/SyntheticPortfolios.jsx"; // New import
import LoginPage from "./components/LoginPage.jsx";
import { useState } from "react";
export default function App() {
  const [user, setUser] = useState(null);
    const [collapsedPanels, setCollapsedPanels] = useState({
      portfolio: false,
      main: false,
      sidebar: false
    });
  
    const handleLogin = (userData) => {
      setUser(userData);
    };
  
    const handleLogout = () => {
      setUser(null);
    };
  
    const togglePanel = (panel) => {
      setCollapsedPanels(prev => ({
        ...prev,
        [panel]: !prev[panel]
      }));
    };
  
    if (!user) {
      return <LoginPage onLogin={handleLogin} />;
    }
  return (
    <div className="app-container">
     <Navbar user={user} onLogout={handleLogout} />
      <div className="app-body">
        <SyntheticPortfolios 
          isCollapsed={collapsedPanels.portfolio}
          onToggle={() => togglePanel('portfolio')}
        />
        <MainDashboard 
          isCollapsed={collapsedPanels.main}
          onToggle={() => togglePanel('main')}
        />
        <Sidebar 
          isCollapsed={collapsedPanels.sidebar}
          onToggle={() => togglePanel('sidebar')}
        />
        {/* </div> */}
      </div>
    </div>
  );
}

