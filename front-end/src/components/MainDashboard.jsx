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

// Initial data for the chart
const initialChartData = {
  labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"],
  datasets: [
    {
      label: "Silver (XAG) Price",
      data: [22.5, 23.0, 24.5, 23.8, 25.0, 27.5, 29.5],
      fill: true,
      backgroundColor: "rgba(192, 192, 192, 0.2)",
      borderColor: "rgba(192, 192, 192, 1)",
      tension: 0.3,
    },
  ],
};

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
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
        color: "#888",
      },
    },
    y: {
      grid: {
        color: "#2a2a2a",
      },
      ticks: {
        color: "#888",
      },
    },
  },
};

export default function MainDashboard() {
  const [chartData, setChartData] = useState(null); // Start as null
  const [performanceMetrics, setPerformanceMetrics] = useState(null); // NEW: State for metrics
  const [silverData, setSilverData] = useState({ price: 29.50, change: -0.32, changePercent: -1.07 }); // Keep static for now
  const [isLoading, setIsLoading] = useState(true);

  // --- FETCHING FROM YOUR PYTHON (Flask) SERVER ---
  useEffect(() => {
    async function fetchData() {
      try {
        setIsLoading(true);
        
        // Fetch both chart data and metrics in parallel
        const [chartResponse, metricsResponse] = await Promise.all([
          fetch("http://127.0.0.1:5000/api/live_chart"),
          fetch("http://127.0.0.1:5000/api/performance_metrics") // NEW fetch
        ]);

        if (!chartResponse.ok || !metricsResponse.ok) {
          throw new Error("Network response was not ok");
        }

        const chartData = await chartResponse.json();
        const metricsData = await metricsResponse.json(); // NEW data

        // --- Set Chart Data ---
        setChartData(chartData);
        
        // --- Update Silver Price in Market Overview ---
        // Get the last price from the "Actual Silver NAV" dataset (index 1)
        if (chartData.datasets[1] && chartData.datasets[1].data.length > 0) {
          const priceData = chartData.datasets[1].data;
          const lastActualPrice = priceData[priceData.length - 1];
          const prevActualPrice = priceData.length > 1 ? priceData[priceData.length - 2] : lastActualPrice;
          
          const change = lastActualPrice - prevActualPrice;
          const changePercent = prevActualPrice === 0 ? 0 : (change / prevActualPrice) * 100;

          setSilverData({ 
            price: lastActualPrice,
            change: change,
            changePercent: changePercent
          });
        }
        
        // --- NEW: Set Performance Metrics ---
        setPerformanceMetrics(metricsData);

      } catch (error) {
        console.error("Error fetching data from Flask:", error);
      } finally {
        setIsLoading(false);
      }
    }

    fetchData();
    
  }, []); // Runs once on component mount

   // Helper function to render the overview
  const renderMarketOverview = () => {
    const isPositive = silverData.change >= 0;
    const changeClass = isPositive ? "positive" : "negative";

    return (
      <div className="market-item-price">
        <span className="market-item-price-val">
          {silverData.price.toFixed(2)}
        </span>
        {/* --- FIXED: Combined into one JSX expression --- */}
        <span className={`market-item-price-change ${changeClass}`}>
          {`${isPositive ? "+" : ""}${silverData.change.toFixed(2)} (${silverData.changePercent.toFixed(2)}%)`}
        </span>
      </div>
    );
  };

  return (
    <div className="main-dashboard">
      {/* --- Market Overview Widget --- */}
      <div className="dashboard-widget">
        <h2 className="dashboard-widget h2">Market Overview</h2>

        {/* S&P 500 (Static) */}
        <div className="market-item">
          <div className="market-item-info">
            <h3 className="market-item-info-name">S&P 500</h3>
            <span className="market-item-info-desc">US Market Index</span>
          </div>
          <div className="market-item-price">
            <span className="market-item-price-val">5,420.10</span>
            <span className="market-item-price-change positive">
              +25.60 (0.47%)
            </span>
          </div>
        </div>

        {/* NASDAQ (Static) */}
        <div className="market-item">
          <div className="market-item-info">
            <h3 className="market-item-info-name">NASDAQ</h3>
            <span className="market-item-info-desc">Tech Market Index</span>
          </div>
          <div className="market-item-price">
            <span className="market-item-price-val">18,105.70</span>
            <span className="market-item-price-change positive">
              +110.20 (0.61%)
            </span>
          </div>
        </div>

        {/* SILVER (XAG) - Now Dynamic */}
        <div className="market-item">
          <div className="market-item-info">
            <h3 className="market-item-info-name">SILVER (XAG)</h3>
            <span className="market-item-info-desc">Spot Price</span>
          </div>
          {/* Rendered by our new function */}
          {isLoading ? <div>Loading...</div> : renderMarketOverview()}
        </div>
      </div>

      {/* --- NEW: Performance Metrics Widget --- */}
      <div className="dashboard-widget">
        <h2 className="dashboard-widget h2">Model Performance (Kalman Filter)</h2>
        {isLoading || !performanceMetrics ? (
          <div>Loading metrics...</div>
        ) : (
          <div className="performance-metrics">
            <div className="metric-item">
              <span className="metric-label">Tracking Error (TE)</span>
              <span className="metric-value">{performanceMetrics.te.toFixed(6)}</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">RMSE</span>
              <span className="metric-value">{performanceMetrics.rmse.toFixed(6)}</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">R-Squared (R²)</span>
              <span className="metric-value">{performanceMetrics.r2.toFixed(4)}</span>
            </div>
          </div>
        )}
      </div>

      {/* --- Price Chart Widget (Title Updated) --- */}
      <div className="dashboard-widget">
        <h2 className="dashboard-widget h2">Kalman Model vs. Actual Silver (NAV)</h2>
        <div className="chart-container">
          {/* Show a loading message until the chart data is fetched */}
          {isLoading || !chartData ? (
            <div>Loading chart data from Python...</div>
          ) : (
            <Line data={chartData} options={chartOptions} />
          )}
        </div>
      </div>
    </div>
  );
}