import React from "react";
// Import its renamed CSS file
import "./SyntheticPortfolios.css";

export default function SyntheticPortfolios() {
  return (
    // Use the "card" class for consistent styling
    <section className="card portfolio-section">
      <h2>Your Synthetic Portfolios</h2>
      <p className="portfolio-subtitle">
        AI-driven asset baskets designed to mimic silver price movements.
      </p>
      <div className="portfolio-cards">
        <div className="portfolio-card">
          <h3>Silver Tracker 1</h3>
          <p>Composition: 40% Copper, 30% Platinum, 30% Nickel</p>
          <button>View Details</button>
        </div>
        <div className="portfolio-card">
          <h3>Silver Mimic AI Model</h3>
          <p>Optimized to follow 92% correlation with silver prices</p>
          <button>Analyze</button>
        </div>
      </div>
    </section>
  );
}
