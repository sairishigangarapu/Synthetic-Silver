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
  // --- Live Chart State ---
  // Put the chart data into state
  const [chartData, setChartData] = useState(initialChartData);

  // --- useEffect for Live Updates ---
  useEffect(() => {
    // Set up an interval to simulate live data
    const interval = setInterval(() => {
      // Use the functional update form of setState to avoid stale state
      setChartData((prevChartData) => {
        // Get the current data and labels from the *previous state*
        const oldLabels = prevChartData.labels;
        const oldDataPoints = prevChartData.datasets[0].data;

        // Create a new label (e.g., current time)
        const newLabel = new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
        });

        // Create a new data point (simulated)
        // Ensure lastPrice is parsed as a float since it might be a string
        const lastPrice = parseFloat(oldDataPoints[oldDataPoints.length - 1]);
        const randomChange = (Math.random() - 0.48) * 0.5; // Small random change
        const newPrice = Math.max(20, lastPrice + randomChange); // Ensure price stays positive

        // Create new arrays, keeping the last 7 points
        const newLabels = [...oldLabels.slice(1), newLabel];
        const newDataPoints = [
          ...oldDataPoints.slice(1),
          newPrice,
        ];

        // Return the new state object
        return {
          labels: newLabels,
          datasets: [
            {
              ...prevChartData.datasets[0], // Keep old styling
              data: newDataPoints,
            },
          ],
        };
      });
    }, 2000); // Update every 2 seconds

    // Cleanup function to stop the interval when the component unmounts
    return () => clearInterval(interval);
  }, []); // Use an empty dependency array so the effect runs only once
  // --- End of Live Chart Logic ---

  return (
    <div className="main-dashboard">
      {/* --- Market Overview Widget --- */}
      <div className="dashboard-widget">
        <h2 className="dashboard-widget h2">Market Overview</h2>

        {/* Improved layout for each market item */}
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

        <div className="market-item">
          <div className="market-item-info">
            <h3 className="market-item-info-name">SILVER (XAG)</h3>
            <span className="market-item-info-desc">Spot Price</span>
          </div>
          <div className="market-item-price">
            <span className="market-item-price-val">29.50</span>
            <span className="market-item-price-change negative">
              -0.32 (1.07%)
            </span>
          </div>
        </div>
      </div>

      {/* --- Price Chart Widget --- */}
      <div className="dashboard-widget">
        <h2 className="dashboard-widget h2">Silver (XAG) Price Chart</h2>
        <div className="chart-container">
          {/* Render the Line chart with the live data from state */}
          <Line data={chartData} options={chartOptions} />
        </div>
      </div>
    </div>
  );
}

