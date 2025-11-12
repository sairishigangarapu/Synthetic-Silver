import pandas as pd
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf  # <-- ADD THIS
import os

# --- GET THE SCRIPT'S OWN DIRECTORY ---
# This makes sure it finds the files, no matter how you run it
basedir = os.path.abspath(os.path.dirname(__file__))

# --- ADD THIS TICKER MAP ---
TICKER_MAP = {
    "COPPER": "HG=F",
    "CORN": "ZC=F",
    "LITHIUM": "LIT",
    "NATURAL_GAS": "NG=F",
    "RARE_EARTH": "REMX",
    "SILVER": "SI=F",
    "SOYBEAN": "ZS=F",
    "WHEAT": "ZW=F"
}
# --- END OF ADDITION ---

# --- File paths ---
CHART_FILE = os.path.join(basedir, 'silver_vs_basket_chart.csv')
CHART_FILE = os.path.join(basedir, 'silver_vs_basket_chart.csv')
METRICS_FILE = os.path.join(basedir, 'silver_vs_basket_metrics.json')
DYNAMIC_WEIGHTS_FILE = os.path.join(basedir, 'dynamic_portfolio_predictions_new.csv')
STATIC_WEIGHTS_FILE = os.path.join(basedir, 'commodity_basket_weights.csv')
ACTUAL_CHART_FILE = os.path.join(basedir, 'silver_vs_actual_chart.csv')
ACTUAL_METRICS_FILE = os.path.join(basedir, 'silver_vs_actual_metrics.json')

# --- Globals to store loaded data ---
chart_data = None
metrics_data = None
dynamic_weights_data = None
static_weights_data = None
# --- ADD THESE TWO NEW GLOBALS ---
actual_chart_data = None
actual_metrics_data = None

# --- Flask App Setup ---
app = Flask(__name__)
CORS(app)

def load_all_data():
    """
    Loads all pre-calculated data from the notebook's
    output files *once* when the server starts.
    """
    global chart_data, metrics_data, dynamic_weights_data, static_weights_data, actual_chart_data, actual_metrics_data
    
    # 1. Load Chart Data
    try:
        df_chart = pd.read_csv(CHART_FILE)
        df_chart["Date"] = pd.to_datetime(df_chart["Date"])
        chart_data = df_chart.set_index("Date").sort_index()
        print(f"✅ Successfully loaded chart data from {CHART_FILE}")
    except Exception as e:
        print(f"❌ ERROR loading chart data: {e}")

    # 2. Load Metrics
    try:
        with open(METRICS_FILE, 'r') as f:
            metrics_data = json.load(f)
        print(f"✅ Successfully loaded metrics from {METRICS_FILE}")
    except Exception as e:
        print(f"❌ ERROR loading metrics data: {e}")
        
    # 3. Load Dynamic Weights (latest row only)
    try:
        df_dynamic = pd.read_csv(DYNAMIC_WEIGHTS_FILE)
        df_dynamic = df_dynamic.set_index("Date").sort_index()
        # Get the last row and convert it to a dict {col: value}
        dynamic_weights_data = df_dynamic.iloc[-1].to_dict()
        print(f"✅ Successfully loaded latest dynamic weights from {DYNAMIC_WEIGHTS_FILE}")
    except Exception as e:
        print(f"❌ ERROR loading dynamic weights: {e}")

    # 4. Load Static Weights
    try:
        df_static = pd.read_csv(STATIC_WEIGHTS_FILE)
        static_weights_data = pd.Series(
            df_static.Raw_Weight.values, 
            index=df_static.Commodity
        ).to_dict()
        print(f"✅ Successfully loaded static weights from {STATIC_WEIGHTS_FILE}")
    except Exception as e:
        print(f"❌ ERROR loading static weights: {e}")

    # 5. Load 'Actual' Chart Data
    try:
        df_chart_actual = pd.read_csv(ACTUAL_CHART_FILE)
        df_chart_actual["Date"] = pd.to_datetime(df_chart_actual["Date"])
        actual_chart_data = df_chart_actual.set_index("Date").sort_index()
        print(f"✅ Successfully loaded 'Actual' chart data from {ACTUAL_CHART_FILE}")
    except Exception as e:
        print(f"❌ ERROR loading 'Actual' chart data: {e}")

    # 6. Load 'Actual' Metrics
    try:
        with open(ACTUAL_METRICS_FILE, 'r') as f:
            actual_metrics_data = json.load(f)
        print(f"✅ Successfully loaded 'Actual' metrics from {ACTUAL_METRICS_FILE}")
    except Exception as e:
        print(f"❌ ERROR loading 'Actual' metrics data: {e}")

# --- API Endpoints ---

@app.route("/")
def home():
    return "Simple Portfolio Server is running!"

@app.route("/api/silver_vs_basket_chart")
def api_silver_vs_basket_chart():
    if chart_data is None:
        return jsonify({"error": "Chart data not loaded."}), 500
    
    # Slicing logic
    timeframe = request.args.get('timeframe', '1Y')
    data = chart_data.copy()
    end_date = data.index.max()
    
    if timeframe == '1D': start_date = end_date - pd.DateOffset(days=1)
    elif timeframe == '5D': start_date = end_date - pd.DateOffset(days=5)
    elif timeframe == '1M': start_date = end_date - pd.DateOffset(months=1)
    elif timeframe == '6M': start_date = end_date - pd.DateOffset(months=6)
    elif timeframe == '1Y': start_date = end_date - pd.DateOffset(years=1)
    elif timeframe == '5Y': start_date = end_date - pd.DateOffset(years=5)
    else: start_date = data.index.min()
    
    sliced_data = data.loc[start_date:end_date]
    
    # Format for Chart.js
    chart_js_data = {
        "labels": sliced_data.index.strftime('%Y-%m-%d').tolist(),
        "datasets": [
            {
                "label": "Silver Predicted Price (NN)",
                "data": sliced_data['Silver_Predicted'].values.tolist(),
                "borderColor": "rgba(88, 166, 255, 1)", 
                "backgroundColor": "rgba(88, 166, 255, 0.2)", 
                "fill": True, "tension": 0.3
            },
            {
                "label": "Commodity Basket Price",
                "data": sliced_data['Basket_Price'].values.tolist(),
                "borderColor": "rgba(192, 192, 192, 1)", 
                "fill": False, "tension": 0.3
            }
        ]
    }
    return jsonify(chart_js_data)

@app.route("/api/silver_vs_basket_metrics")
def api_silver_vs_basket_metrics():
    if metrics_data is None:
        return jsonify({"error": "Metrics data not loaded."}), 500
    return jsonify(metrics_data)

@app.route("/api/dynamic_weights")
def api_dynamic_weights():
    if dynamic_weights_data is None:
        return jsonify({"error": "Dynamic weights not loaded."}), 500
    return jsonify(dynamic_weights_data)

@app.route("/api/static_weights")
def api_static_weights():
    if static_weights_data is None:
        return jsonify({"error": "Static weights not loaded."}), 500
    return jsonify(static_weights_data)

@app.route("/api/latest_prices")
def api_latest_prices():
    """
    Fetches the latest prices for commodities in the Ticker Map.
    """
    try:
        symbols = list(TICKER_MAP.values())
        # yf.download is faster for multiple tickers
        data = yf.download(tickers=symbols, period="2d", interval="1d")

        if data.empty:
            return jsonify({"error": "No data found from Yahoo Finance"}), 500

        # Get the most recent 'Close' price for each
        latest_prices = data['Close'].iloc[-1].to_dict()

        # Map tickers back to commodity names
        reverse_map = {v: k for k, v in TICKER_MAP.items()}
        price_list = []

        for ticker, price in latest_prices.items():
            if pd.isna(price):
                continue

            name = reverse_map.get(ticker, ticker)
            price_list.append({
                "name": name.capitalize(),
                "symbol": ticker,
                "price": price
            })

        return jsonify(price_list)

    except Exception as e:
        print(f"Error in /api/latest_prices: {e}")
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/silver_vs_actual_chart")
def api_silver_vs_actual_chart():
    if actual_chart_data is None:
        return jsonify({"error": "Actual chart data not loaded."}), 500

    # Slicing logic
    timeframe = request.args.get('timeframe', '6M')
    data = actual_chart_data.copy()
    end_date = data.index.max()

    if timeframe == '1D': start_date = end_date - pd.DateOffset(days=1)
    elif timeframe == '5D': start_date = end_date - pd.DateOffset(days=5)
    elif timeframe == '1M': start_date = end_date - pd.DateOffset(months=1)
    elif timeframe == '6M': start_date = end_date - pd.DateOffset(months=6)
    elif timeframe == '1Y': start_date = end_date - pd.DateOffset(years=1)
    elif timeframe == '5Y': start_date = end_date - pd.DateOffset(years=5)
    else: start_date = data.index.min()

    sliced_data = data.loc[start_date:end_date]

    # Format for Chart.js
    chart_js_data = {
        "labels": sliced_data.index.strftime('%Y-%m-%d').tolist(),
        "datasets": [
            {
                "label": "Silver Predicted Price (NN)",
                "data": sliced_data['Silver_Predicted'].values.tolist(),
                "borderColor": "rgba(88, 166, 255, 1)", 
                "backgroundColor": "rgba(88, 166, 255, 0.2)",
                "fill": True,
                "tension": 0.3
            },
            {
                "label": "Actual Silver Price",
                "data": sliced_data['Silver_Actual'].values.tolist(),
                "borderColor": "rgba(192, 192, 192, 1)",
                "fill": False,
                "tension": 0.3
            }
        ]
    }
    return jsonify(chart_js_data)

@app.route("/api/silver_vs_actual_metrics")
def api_silver_vs_actual_metrics():
    if actual_metrics_data is None:
        return jsonify({"error": "Actual metrics data not loaded."}), 500
    return jsonify(actual_metrics_data)

# --- Run the Server ---
if __name__ == "__main__":
    load_all_data()
    app.run(debug=True, port=5000)