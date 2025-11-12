import React, { useState, useEffect } from "react";
import "./LoginPage.css";


export default function LoginPage({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSignup, setIsSignup] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    // Simple validation - in production, we'd verify credentials
    if (email && password) {
      onLogin({ email, isAuthenticated: true });
    }
  }


  return (
    <div className="login-container">
      <div className="login-card">
        <h1 className="login-title">Synthetic Commodities</h1>
        <h2 className="login-subtitle">{isSignup ? "Create Account" : "Welcome Back"}</h2>
        
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
            />
          </div>
          
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
            />
          </div>
          
          <button type="submit" className="login-button">
            {isSignup ? "Sign Up" : "Login"}
          </button>
        </form>
        
        <p className="toggle-auth">
          {isSignup ? "Already have an account? " : "Don't have an account? "}
          <span onClick={() => setIsSignup(!isSignup)}>
            {isSignup ? "Login" : "Sign Up"}
          </span>
        </p>
      </div>
    </div>
  );
};
