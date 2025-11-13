import React, { useState, useEffect } from "react";
import { Line } from "react-chartjs-2";
import "./MainDashboard.css"; // Corrected path
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);


const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
  legend: {
    display: true,
    labels: {
      color: '#c9d1d9', // This KEEPS your text readable
      displayColors: true,
      // --- ADD THESE TWO LINES ---

      boxWidth: 8
      // --- END OF NEW LINES ---
    }
  },

    tooltip: {
      mode: "index",
      intersect: false,
    },
  },
  scales: {
    x: {
      grid: {
        display: false,
      },
      ticks: {
        color: "#8b949e", // Lighter grey, from your theme
        autoSkip: true,     // <-- 1. This is the magic part
        maxRotation: 45,     // <-- 2. Forces horizontal labels
        padding: 10,        // <-- Adds some space
        maxTicksLimit: 15 // <-- ADD THIS LINE
      },
    },
    y: {
      grid: {
        color: "#30363d", // Use your standard border color
        drawBorder: false,
      },
      ticks: {
        color: "#8b949e", // Lighter grey
        padding: 10,
      },
    },
  },
  // --- ADD THIS ENTIRE SECTION ---
  elements: {
    point: {
      radius: 0, // <-- 3. Hides all points by default
      hoverRadius: 5, // <-- 4. Shows a point on hover
      hoverBorderColor: 'white',
      hoverBackgroundColor: '#58a6ff' // A blue from your theme
    },
    line: {
      tension: 0.3 // This will smooth the line slightly
    }
  }
  // --- END OF NEW SECTION ---
};

export default function MainDashboard({ isCollapsed, onToggle }) {
  const [chartData, setChartData] = useState(null); // Start as null
  const [performanceMetrics, setPerformanceMetrics] = useState(null); // NEW: State for metrics
  const [commodityPrices, setCommodityPrices] = useState([]); // NEW: State for basket prices
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingPrices, setIsLoadingPrices] = useState(true); // NEW: Separate loading for prices
  const [chartMode, setChartMode] = useState('BASKET'); // 'BASKET' or 'ACTUAL'
  const [timeframe, setTimeframe] = useState('1Y'); // NEW: Timeframe feature
  const timeframes = ['1D', '5D', '1M', '6M','1Y','5Y','MAX'];
  // --- FETCHING FROM YOUR PYTHON (Flask) SERVER ---
useEffect(() => {
  async function fetchChartAndMetrics() {
    try {
      setIsLoading(true);

      // Define which endpoints to call based on chartMode
      let chartUrl = '';
      let metricsUrl = '';

      if (chartMode === 'BASKET') {
        chartUrl = `http://127.0.0.1:5000/api/silver_vs_basket_chart?timeframe=${timeframe}`;
        metricsUrl = "http://127.0.0.1:5000/api/silver_vs_basket_metrics";
      } else { // chartMode === 'ACTUAL'
        chartUrl = `http://127.0.0.1:5000/api/silver_vs_actual_chart?timeframe=${timeframe}`;
        metricsUrl = "http://127.0.0.1:5000/api/silver_vs_actual_metrics";
      }

      // Fetch chart and metrics in parallel
      const [chartResponse, metricsResponse] = await Promise.all([
        fetch(chartUrl),
        fetch(metricsUrl)
      ]);

      if (!chartResponse.ok) throw new Error("Chart network response was not ok");
      if (!metricsResponse.ok) throw new Error("Metrics network response was not ok");

      const chartData = await chartResponse.json();
      const metricsData = await metricsResponse.json();

      setChartData(chartData);
      setPerformanceMetrics(metricsData);

    } catch (error) {
      console.error("Error fetching data from Flask:", error);
    } finally {
      setIsLoading(false);
    }
  }
  fetchChartAndMetrics();

  // Add chartMode to the dependency array
}, [timeframe, chartMode]); // <-- UPDATED


  return (
    <div className={`panel-container main ${isCollapsed ? 'collapsed' : ''}`}>
      {!isCollapsed && (
        <div className="main-dashboard">
        {/* --- Price Chart Widget (Title Updated) --- */}
        <div className="dashboard-widget">
          {/* --- ADDED: Header to hold title and buttons --- */}
          {/* --- NEW: Title and Dropdown Container --- */}
          <div className="widget-header">
            {/* --- NEW: The <select> element IS the title --- */}
            <select 
              className="chart-title-dropdown" 
              value={chartMode} 
              onChange={(e) => setChartMode(e.target.value)}
            >
              <option value="BASKET">Silver Predicted Price vs. Basket Price</option>
              <option value="ACTUAL">Silver Predicted Price vs. Actual Price</option>
            </select>
            {/* --- END OF NEW BLOCK --- */}
            {/* --- ADDED: Timeframe Buttons --- */}
            <div className="timeframe-selector">
              <div className="timeframe-selector">
                {timeframes.map((tf) => (
                  <button
                    key={tf}
                    className={`timeframe-btn ${timeframe === tf ? 'active' : ''}`}
                    onClick={() => setTimeframe(tf)}
                  >
                    {tf}
                  </button>
                ))}
              </div>
            </div>
          </div>
          <div className="chart-container">
            {isLoading || !chartData ? (
              <div className="chart-loading">Loading chart data from Python...</div>
            ) : (
              <Line data={chartData} options={chartOptions} />
            )}
          </div>
        </div>
        
        {/* --- NEW: Performance Metrics Widget --- */}
        {/* --- Dynamic Metrics Widget --- */}
        <div className="dashboard-widget">
          <h2 className="dashboard-widget h2">
            {chartMode === 'BASKET' ? 'Silver vs. Basket Analysis' : 'Predicted vs. Actual Analysis'}
          </h2>

          {isLoading || !performanceMetrics ? (
            <div>Loading metrics...</div>
          ) : (
            <div className="performance-metrics">
              {/* Show metrics for 'BASKET' mode */}
              {chartMode === 'BASKET' && (
                <>
                  <div className="metric-item">
                    <span className="metric-label">MAE (vs. Basket)</span>
                    <span className="metric-value">{performanceMetrics.mae_silver_vs_basket?.toFixed(4)}</span>
                  </div>
                  <div className="metric-item">
                    <span className="metric-label">MSE (vs. Basket)</span>
                    <span className="metric-value">{performanceMetrics.mse_silver_vs_basket?.toFixed(4)}</span>
                  </div>
                  <div className="metric-item">
                    <span className="metric-label">R-Squared (vs. Basket)</span>
                    <span className="metric-value">{performanceMetrics.r2_silver_vs_basket?.toFixed(4)}</span>
                  </div>
                </>
              )}

              {/* Show metrics for 'ACTUAL' mode */}
              {chartMode === 'ACTUAL' && (
                <>
                  <div className="metric-item">
                    <span className="metric-label">MAE (vs. Actual)</span>
                    <span className="metric-value">{performanceMetrics.mae_silver_vs_actual?.toFixed(4)}</span>
                  </div>
                  <div className="metric-item">
                    <span className="metric-label">MSE (vs. Actual)</span>
                    <span className="metric-value">{performanceMetrics.mse_silver_vs_actual?.toFixed(4)}</span>
                  </div>
                  <div className="metric-item">
                    <span className="metric-label">R-Squared (vs. Actual)</span>
                    <span className="metric-value">{performanceMetrics.r2_silver_vs_actual?.toFixed(4)}</span>
                  </div>
                </>
              )}
            </div>
          )}
        </div>

        {/* --- Silver vs. Basket Metrics Widget --- */}
        {/* <div className="dashboard-widget">
          <h2 className="dashboard-widget h2">Silver vs. Basket Analysis Metrics</h2>
          {isLoading || !performanceMetrics ? (
            <div>Loading metrics...</div>
          ) : (
            <div className="performance-metrics">
              <div className="metric-item">
                <span className="metric-label">MAE (vs. Basket)</span>
                <span className="metric-value">{performanceMetrics.silver_mean_silver_vs_basket?.toFixed(4)}</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">MSE (vs. Basket)</span>
                <span className="metric-value">{performanceMetrics.mse_silver_vs_basket?.toFixed(4)}</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">R-Squared (vs. Basket)</span>
                <span className="metric-value">{performanceMetrics.r2_silver_vs_basket?.toFixed(4)}</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Mean Prices</span>
                <span className="metric-value">Silver: {performanceMetrics.silver_mean_silver_vs_basket?.toFixed(4)} 
                  <br></br>
                                              Basket: {performanceMetrics.basket_mean_silver_vs_basket?.toFixed(4)} 
                                              </span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Mean Difference</span>
                <span className="metric-value">{performanceMetrics.Mean_Difference?.toFixed(4)}</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">SD of Difference</span>
                <span className="metric-value">{performanceMetrics.Std_Dev_of_Difference?.toFixed(4)}</span>
              </div>
            </div>
          )}
        </div> */}
        {/* --- Basket Overview Widget --- */}
        {/* <div className="dashboard-widget">
          <h2 className="dashboard-widget h2">Basket Commodities (Live Prices)</h2>
          <div className="market-list">
            {isLoadingPrices ? (
              <div>Loading prices...</div>
            ) : (
              commodityPrices.map((item) => (
                <div className="market-item" key={item.symbol}>
                  <div className="market-item-info">
                    <h3 className="market-item-info-name">{item.name}</h3>
                    <span className="market-item-info-desc">{item.name}</span>
                  </div>
                  <div className="market-item-price">
                    <span className="market-item-price-val">
                      ${item.price?.toFixed(2)}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div> */}
      </div>
    )}
    </div>
  );
}