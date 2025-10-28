import React, { useState, useEffect } from "react";
import "./Sidebar.css";

// Mock data for the ticker
const initialTickerData = [
  { symbol: "SLV", name: "Silver ETF", price: 27.20, change: 0.15, changePerc: 0.55 },
  { symbol: "COPX", name: "Copper Miners", price: 52.80, change: -0.40, changePerc: -0.75 },
  { symbol: "PPLT", name: "Platinum ETF", price: 89.10, change: 1.05, changePerc: 1.19 },
  { symbol: "NICK", name: "Nickel ETF", price: 18.45, change: -0.05, changePerc: -0.27 },
  { symbol: "ZINC", name: "Zinc Miners", price: 31.50, change: 0.22, changePerc: 0.70 },
  { symbol: "GOLD", name: "Gold ETF", price: 215.30, change: 1.10, changePerc: 0.51 },
  { symbol: "USO", name: "Oil Fund", price: 78.90, change: -1.20, changePerc: -1.50 },
];

export default function Sidebar() {
  const [tickerData, setTickerData] = useState(initialTickerData);

  // Simulate live price updates
  useEffect(() => {
    const interval = setInterval(() => {
      setTickerData((prevData) =>
        prevData.map((stock) => {
          const randomChange = (Math.random() - 0.5) * 0.2; // Small random fluctuation
          const newPrice = Math.max(0, parseFloat((stock.price + randomChange).toFixed(2)));
          const newChange = parseFloat((newPrice - stock.price + stock.change).toFixed(2));
          const newChangePerc = parseFloat(((newChange / (newPrice - newChange)) * 100).toFixed(2));
          
          return {
            ...stock,
            price: newPrice,
            change: newChange,
            changePerc: newChangePerc,
          };
        })
      );
    }, 2000); // Update every 2 seconds

    return () => clearInterval(interval); // Clean up on unmount
  }, []);

  return (
    <aside className="sidebar">
      {/* Ticker List Card */}
      <div className="card">
        <h3 className="sidebar-title">Market Ticker</h3>
        <ul className="ticker-list">
          {tickerData.map((stock) => (
            <li className="ticker-item" key={stock.symbol}>
              <div className="ticker-symbol-name">
                <span className="ticker-symbol">{stock.symbol}</span>
                <span className="ticker-name">{stock.name}</span>
              </div>
              <div className="ticker-price-change">
                <span className="ticker-price">${stock.price.toFixed(2)}</span>
                <span className={stock.change >= 0 ? "change-positive" : "change-negative"}>
                  {stock.change >= 0 ? "+" : ""}
                  {stock.change.toFixed(2)} ({stock.changePerc.toFixed(2)}%)
                </span>
              </div>
            </li>
          ))}
        </ul>
      </div>
      
      {/* Another sidebar module, e.g., Top Movers */}
      <div className="card">
        <h3 className="sidebar-title">Top Movers</h3>
        <ul className="ticker-list">
          {/* Static mock data for this one */}
           <li className="ticker-item">
              <span className="ticker-symbol">PPLT</span>
              <span className="ticker-price">$89.10</span>
              <span className="change-positive">+1.19%</span>
           </li>
           <li className="ticker-item">
              <span className="ticker-symbol">USO</span>
              <span className="ticker-price">$78.90</span>
              <span className="change-negative">-1.50%</span>
           </li>
        </ul>
      </div>
    </aside>
  );
}
