import React, { useState, useEffect } from "react";
import "./SyntheticPortfolios.css"; // Ignoring path error as requested

// --- NEW Modal Component ---
// We define this inside the same file to keep things simple
const Modal = ({ data, onClose }) => {
  if (!data) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close-btn" onClick={onClose}>
          &times;
        </button>
        <h3 className="modal-title">{data.title}</h3>
        <p className="modal-desc">{data.description}</p>
        
        {/* Check if we have weights to display */}
        {data.weights && (
          <div className="portfolio-weights modal-weights">
            <strong>Live Composition:</strong>
            <ul>
              {Object.entries(data.weights).map(([asset, weight]) => (
                <li key={asset}>
                  <span className="asset-name">{asset.charAt(0).toUpperCase() + asset.slice(1)}:</span>
                  <span className="asset-weight">{(weight * 100).toFixed(2)}%</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Check for other details (for the Kalman model) */}
        {data.details && (
          <div className="portfolio-details">
            <strong>Model Details:</strong>
            <p>{data.details}</p>
          </div>
        )}
      </div>
    </div>
  );
};


// --- Updated PortfolioCard Component ---
// It now accepts an `onViewDetails` function
const PortfolioCard = ({ title, description, weights, onViewDetails }) => (
  <div className="dashboard-widget portfolio-card">
    <h3 className="dashboard-widget h3">{title}</h3>
    <p className="portfolio-desc">{description}</p>
    
    {weights && (
      <div className="portfolio-weights">
        <strong>Composition:</strong>
        <ul>
          {Object.entries(weights).map(([asset, weight]) => (
            <li key={asset}>
              <span className="asset-name">{asset.charAt(0).toUpperCase() + asset.slice(1)}:</span>
              <span className="asset-weight">{(weight * 100).toFixed(2)}%</span>
            </li>
          ))}
        </ul>
      </div>
    )}
    
    {/* This button now calls the function passed to it */}
    <button className="portfolio-btn" onClick={onViewDetails}>
      View Details
    </button>
  </div>
);

export default function SyntheticPortfolios() {
  const [staticWeights, setStaticWeights] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  
  // --- NEW State for the modal ---
  const [modalData, setModalData] = useState(null);

  useEffect(() => {
    async function fetchStaticWeights() {
      try {
        setIsLoading(true);
        const response = await fetch("http://127.0.0.1:5000/api/static_weights");
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        const data = await response.json();
        setStaticWeights(data);
      } catch (error) {
        console.error("Error fetching static weights from Flask:", error);
      } finally {
        setIsLoading(false);
      }
    }
    fetchStaticWeights();
  }, []);

  // --- NEW handler functions for the modal ---
  const handleViewDetails = (data) => {
    setModalData(data);
  };
  
  const handleCloseModal = () => {
    setModalData(null);
  };

  // Mock data for the Kalman model card to show in its modal
  const kalmanDetails = {
    title: "Silver Mimic AI (Kalman)",
    description: "Dynamic weights optimized for 92% correlation.",
    details: "This model uses a Kalman Filter to update asset weights in real-time, reacting to market changes to provide a more accurate mimic of silver's price movements. The chart in the center column shows the performance of this model."
  };

  return (
    <div className="portfolio-main">
      <h2 className="dashboard-widget h2">Your Synthetic Portfolios</h2>
      <p className="portfolio-main-desc">
        AI-driven asset baskets designed to mimic silver price movements.
      </p>

      {/* --- Dynamic Card --- */}
      {isLoading ? (
        <div>Loading portfolio...</div>
      ) : (
        <PortfolioCard 
          title="Silver Tracker 1 (QP Model)" 
          description="Static basket from Constrained QP model."
          weights={staticWeights}
          // Pass the handler to the button
          onViewDetails={() => handleViewDetails({
            title: "Silver Tracker 1 (QP Model)",
            description: "This portfolio uses a static basket of assets calculated by a Quadratic Programming (QP) optimization model. The weights are fixed and optimized based on historical training data to minimize tracking error.",
            weights: staticWeights
          })}
        />
      )}

      {/* --- Static Card (for comparison) --- */}
      <PortfolioCard 
        title="Silver Mimic AI (Kalman)" 
        description="Dynamic weights optimized for 92% correlation."
        // Pass the handler to this button too
        onViewDetails={() => handleViewDetails(kalmanDetails)}
      />

      {/* --- NEW: Render the modal if modalData is not null --- */}
      <Modal data={modalData} onClose={handleCloseModal} />
    </div>
  );
}