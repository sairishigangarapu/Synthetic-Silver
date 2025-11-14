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

export default function SyntheticPortfolios ({ isCollapsed, onToggle }) {
  const [staticWeights, setStaticWeights] = useState(null);
  const [dynamicWeights, setDynamicWeights] = useState(null); // <-- ADDED THIS
  const [livePrices, setLivePrices] = useState([]); // New state for prices
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingPrices, setIsLoadingPrices] = useState(true); // New loading state
  const [isLoadingDynamic, setIsLoadingDynamic] = useState(true); // <-- ADDED THIS
  
  // --- NEW State for the modal ---
  const [modalData, setModalData] = useState(null);

  useEffect(() => {
    async function fetchAllWeights() {
      try {
        setIsLoading(true);
        setIsLoadingDynamic(true);

        const [staticResponse, dynamicResponse] = await Promise.all([
          fetch("http://127.0.0.1:5000/api/static_weights"),
          fetch("http://127.0.0.1:5000/api/dynamic_weights") // <-- UPDATED
        ]);

        if (!staticResponse.ok) throw new Error("Static weights network response was not ok");
        if (!dynamicResponse.ok) throw new Error("Dynamic weights network response was not ok");

        const staticData = await staticResponse.json();
        const dynamicData = await dynamicResponse.json(); // <-- NEW

        setStaticWeights(staticData);
        setDynamicWeights(dynamicData); // <-- NEW

      } catch (error) {
        console.error("Error fetching portfolio weights from Flask:", error);
      } finally {
        setIsLoading(false);
        setIsLoadingDynamic(false); // <-- NEW
      }
    }
    // --- NEW Function to fetch prices ---
    async function fetchLivePrices() {
      try {
        setIsLoadingPrices(true);
        const response = await fetch("http://127.0.0.1:5000/api/latest_prices");
        if (!response.ok) {
          throw new Error("Live prices network response was not ok");
        }
        const data = await response.json();
        setLivePrices(data);
      } catch (error) {
        console.error("Error fetching live prices:", error);
      } finally {
        setIsLoadingPrices(false);
      }
    }

    fetchLivePrices();
    fetchAllWeights();
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
    <div className={`panel-container ${isCollapsed ? 'collapsed' : ''}`}>
      <button className="collapse-btn left" onClick={onToggle}>
        {isCollapsed ? '→' : '←'}
      </button>
      
    <div className="portfolios">
          <h2 className="portfolios-title">Your Synthetic Portfolios</h2>
          <p className="portfolios-desc">
            AI-driven asset baskets designed to mimic silver price movements.
          </p>

      {/* --- Dynamic Card --- */}
      {/* {isLoading ? (
        <div>Loading portfolio...</div>
      ) : (
        <PortfolioCard 
          title="Static Portfolio (Baseline)" // <-- UPDATED
          description="Baseline weights from commodity basket analysis." // <-- UPDATED
          weights={staticWeights}
          onViewDetails={() => handleViewDetails({
            title: "Static Portfolio (Baseline)",
            description: "These are static weights derived from the 'commodity_basket_weights.csv' file, representing a baseline portfolio.", // <-- UPDATED
            weights: staticWeights
          })}
        />
      )} */}


      {/* --- Dynamic NN Card --- */}
      {isLoadingDynamic ? (
        <div>Loading NN portfolio...</div>
      ) : (
        <PortfolioCard 
          title="Dynamic Portfolio (NN Model)" // <-- UPDATED
          description="Live weights from predictive NN." // <-- UPDATED
          weights={dynamicWeights} // <-- USE NEW STATE
          onViewDetails={() => handleViewDetails({
            title: "Dynamic Portfolio (NN Model)",
            description: "These are the latest weights predicted *live* by the Neural Network, based on 8 parametric features from future price data. Weights are capped at 30% per asset.", // <-- UPDATED
            weights: dynamicWeights
          })}
        />
      )}
      {/* --- *** NEW LIVE PRICES CARD *** --- */}
          <div className="portfolio-card">
            <h3 className="dashboard-widget h3">Live Commodity Prices</h3>
            {isLoadingPrices ? (
              <div>Loading prices...</div>
            ) : (
              <ul className="live-price-list">
                {livePrices.map((item) => (
                  <li className="live-price-item" key={item.symbol}>
                    <span className="live-asset-name">{item.name}</span>
                    <span className="live-asset-price">
                      ${item.price.toFixed(2)}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
          {/* --- *** END OF NEW CARD *** --- */}
          
      {/* --- NEW: Render the modal if modalData is not null --- */}
      <Modal data={modalData} onClose={handleCloseModal} />
    </div>
    </div>
  );
}