import os
import math
import numpy as np
import pandas as pd
import yfinance as yf  # <-- **ADD THIS IMPORT**
from flask import Flask, jsonify
from flask_cors import CORS
from sklearn.metrics import r2_score, mean_squared_error
import cvxpy as cp
from pykalman import KalmanFilter

# --- Flask App Setup ---
app = Flask(__name__)
CORS(app)  # Allow React frontend to call this server

# --- Globals to store results ---
QP_WEIGHTS = None
KALMAN_CHART_DATA = None
KALMAN_METRICS = None  # NEW: Global for performance metrics

# --- File paths and Configs (from your notebook) ---
FILE_MAP = {
    "silver": "./silver.csv",   # TARGET
    "gold": "./gold.csv",
    "copper": "./copper.csv",
    "lead": "./lead.csv",
    "nickel": "./nickel.csv",
    "zinc": "./zinc.csv",
}
DATE_COL, PRICE_COL = "Date", "Price"
TRAIN_END = "2021-12-31"
VAL_START, VAL_END = "2022-01-01", "2023-12-31"
TEST_START, TEST_END = "2024-01-01", "2024-08-29"
TARGET = "silver"

# --- NEW: Yahoo Finance Ticker Mapping ---
# Maps your asset names to their Yahoo Finance symbols
TICKER_MAP = {
    "silver": "SI=F",
    "gold": "GC=F",
    "copper": "HG=F",
    "lead": "LRE",   # <-- Use LSE ticker
    "nickel": "NIX.CN", # <-- Use LSE ticker
    "zinc": "ZINC.L"    # <-- Use LSE ticker
}
# Get just the X_cols (assets in our basket, excluding silver)
X_COLS_NAMES = [key for key in FILE_MAP.keys() if key != TARGET]


# --- Helper Functions (from your notebook) ---
# (read_price_series, to_log_returns, align_on_intersection, etc. remain the same)
def read_price_series(path, date_col=DATE_COL, px_col=PRICE_COL, dayfirst=True):
    df = pd.read_csv(path)[[date_col, px_col]].copy()
    df[date_col] = pd.to_datetime(df[date_col], dayfirst=dayfirst, errors="coerce")
    df = df.dropna(subset=[date_col]).sort_values(date_col)
    df = df.drop_duplicates(subset=[date_col], keep='last').set_index(date_col)
    df.columns = [px_col]
    df = df.replace([np.inf, -np.inf], np.nan).dropna()
    df = df[df[px_col] > 0]
    return df

def to_log_returns(px_df, col=PRICE_COL):
    r = np.log(px_df[col] / px_df[col].shift(1))
    return r.to_frame(name="ret").dropna()

def align_on_intersection(ret_dict):
    keys = list(ret_dict.keys())
    base = ret_dict[keys[0]].copy(); base.columns = [keys[0]]
    for k in keys[1:]:
        tmp = ret_dict[k].copy(); tmp.columns = [k]
        base = base.join(tmp, how="inner")
    return base.sort_index()

def winsorize_by_quantiles(df, lower=0.01, upper=0.99, ref_index=None):
    out = df.copy()
    for c in out.columns:
        if ref_index is not None and len(ref_index) > 0:
            q_lo = out.loc[ref_index, c].quantile(lower)
            q_hi = out.loc[ref_index, c].quantile(upper)
        else:
            q_lo = out[c].quantile(lower); q_hi = out[c].quantile(upper)
        out[c] = out[c].clip(q_lo, q_hi)
    return out

def nav_from_logrets(log_ret, start_nav=100.0):
    simple = np.exp(log_ret) - 1.0
    return (1.0 + simple).cumprod() * start_nav

def tracking_error(y_true, y_pred):
    resid = (y_true - y_pred).dropna()
    return float(resid.std(ddof=1))

def run_kalman(R, y, q, r, init_w=None):
    T, N = R.shape
    if init_w is None:
        init_w = np.ones(N) / N
    transition_matrices = np.eye(N)
    observation_matrices = R.reshape((-1, 1, N))
    kf = KalmanFilter(
        n_dim_state=N, n_dim_obs=1,
        transition_matrices=transition_matrices,
        observation_matrices=observation_matrices,
        transition_covariance=q * np.eye(N),
        observation_covariance=np.array([[r]]),
        initial_state_mean=init_w,
        initial_state_covariance=np.eye(N)
    )
    means, covs = kf.filter(y.reshape(-1,1))
    yhat = np.einsum("tn,tn->t", R, means.squeeze())
    return means.squeeze(), yhat


# --- Model Functions (to be run once at startup) ---
# (load_data, train_qp_model, train_kalman_model remain the same as your file)
def load_data():
    """
    Loads and processes all data from CSV files.
    This is from Cell 2 of your notebook.
    """
    try:
        series_px = {}
        for k, fname in FILE_MAP.items():
            if not os.path.exists(fname):
                raise FileNotFoundError(f"Missing file: {fname}. Please add it to the directory.")
            series_px[k] = read_price_series(fname)
        
        series_ret = {}
        for k, df in series_px.items():
            series_ret[k] = to_log_returns(df)
            series_ret[k].columns = [k]
            
        panel = align_on_intersection(series_ret)
        
        train_mask = (panel.index <= pd.to_datetime(TRAIN_END))
        val_mask   = (panel.index >= pd.to_datetime(VAL_START)) & (panel.index <= pd.to_datetime(VAL_END))
        test_mask  = (panel.index >= pd.to_datetime(TEST_START)) & (panel.index <= pd.to_datetime(TEST_END))
        
        panel_w = winsorize_by_quantiles(panel, 0.01, 0.99, ref_index=panel.index[train_mask])
        
        X_cols = [c for c in panel.columns if c != TARGET]
        
        train_df = panel_w.loc[train_mask].copy()
        val_df   = panel_w.loc[val_mask].copy()
        test_df  = panel_w.loc[test_mask].copy()
        
        trainval_mask = (panel_w.index <= pd.to_datetime(VAL_END))
        X_trainval, y_trainval = panel_w.loc[trainval_mask, X_cols], panel_w.loc[trainval_mask, TARGET]
        
        R_full  = panel_w[X_cols].values
        y_full  = panel_w[TARGET].values
        times   = panel_w.index
        test_mask_full = (times >= pd.to_datetime(TEST_START)) & (times <= pd.to_datetime(TEST_END))
        
        return X_trainval, y_trainval, X_cols, R_full, y_full, times, test_mask_full, y_full[test_mask_full]

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None

def train_qp_model(X_trainval, y_trainval, X_cols):
    """
    Trains the Constrained QP model from Cell 3.
    Returns the final static weights.
    """
    L_leverage, weight_cap, lambda_l2 = 2.0, 0.90, 1e-6
    X, y, N = X_trainval.values, y_trainval.values, X_trainval.shape[1]
    w, c, ones = cp.Variable(N), cp.Variable(), np.ones(X.shape[0])
    
    pred = X @ w + c * ones
    mse = cp.sum_squares(y - pred) / X.shape[0]
    objective = cp.Minimize(mse + lambda_l2 * cp.sum_squares(w))
    constraints = [w >= 0, cp.sum(w) <= L_leverage, w <= weight_cap]
    prob = cp.Problem(objective, constraints)
    
    try:
        prob.solve(solver=cp.OSQP, verbose=False)
    except Exception:
        prob.solve(solver=cp.SCS, verbose=False)
        
    if w.value is None:
        return {"error": "QP model failed to solve."}
        
    w_star = pd.Series(np.asarray(w.value).ravel(), index=X_cols)
    return w_star.to_dict()

def train_kalman_model(R_full, y_full, times, test_mask_full, y_test_true):
    """
    Trains the Kalman Filter model from Cell 4.
    Returns Chart.js formatted data AND performance metrics.
    """
    # Best params from your notebook
    best_params = {'te': 0.007867, 'q': 0.0001, 'r': 1e-05}
    
    means_best, yhat_best = run_kalman(R_full, y_full, q=best_params["q"], r=best_params["r"])
    
    # Get the test predictions
    yhat_test_kf  = pd.Series(yhat_best[test_mask_full], index=times[test_mask_full])
    y_test_kf     = pd.Series(y_test_true, index=times[test_mask_full])

    # Convert log returns to NAV for plotting
    nav_pred = nav_from_logrets(yhat_test_kf)
    nav_true = nav_from_logrets(y_test_kf)

    # Format for Chart.js
    chart_js_data = {
        "labels": nav_pred.index.strftime('%Y-%m-%d').tolist(), # Dates for X-axis
        "datasets": [
            {
                "label": "Synthetic NAV (Kalman)",
                "data": nav_pred.values.tolist(),
                "fill": True,
                "backgroundColor": "rgba(88, 166, 255, 0.2)",
                "borderColor": "rgba(88, 166, 255, 1)",
                "tension": 0.3,
            },
            {
                "label": "Actual Silver NAV",
                "data": nav_true.values.tolist(),
                "fill": False,
                "borderColor": "rgba(192, 192, 192, 1)",
                "tension": 0.3,
            }
        ]
    }
    
    # --- NEW: Calculate Performance Metrics ---
    te = tracking_error(y_test_kf, yhat_test_kf)
    rmse = math.sqrt(mean_squared_error(y_test_kf, yhat_test_kf))
    r2 = r2_score(y_test_kf, yhat_test_kf)
    metrics = {"te": te, "rmse": rmse, "r2": r2}

    return chart_js_data, metrics # Return both

# --- Main Server Logic ---
def load_all_models():
    global QP_WEIGHTS, KALMAN_CHART_DATA, KALMAN_METRICS
    
    data = load_data()
    if data is None:
        print("Failed to load data. Server will run with mock data.")
        # Fallback to mock data if CSVs are missing
        QP_WEIGHTS = {"gold": 0.90, "copper": 0.10}
        KALMAN_CHART_DATA = {"labels": ["T-1"], "datasets": [{"label": "Error", "data": [0]}]}
        KALMAN_METRICS = {"te": 0, "rmse": 0, "r2": 0}
        return
        
    X_trainval, y_trainval, X_cols, R_full, y_full, times, test_mask_full, y_test_true = data
    print("Data loaded successfully.")

    # --- 2. Train QP Model ---
    print("Training QP model...")
    QP_WEIGHTS = train_qp_model(X_trainval, y_trainval, X_cols)
    print(f"QP Weights calculated: {QP_WEIGHTS}")

    # --- 3. Train Kalman Model ---
    print("Training Kalman Filter model...")
    KALMAN_CHART_DATA, KALMAN_METRICS = train_kalman_model(R_full, y_full, times, test_mask_full, y_test_true)
    print("Kalman chart data calculated.")
    print(f"Kalman metrics calculated: {KALMAN_METRICS}")
    
    print("\n--- All models loaded. Server is ready. ---")


# --- API Endpoints (The "Connection" Points) ---

@app.route("/")
def home():
    return "Python Backend Server is running!"

@app.route("/api/static_weights")
def api_static_weights():
    if QP_WEIGHTS is None:
        return jsonify({"error": "Model is not loaded."}), 500
    return jsonify(QP_WEIGHTS)

@app.route("/api/live_chart")
def api_live_chart():
    if KALMAN_CHART_DATA is None:
        return jsonify({"error": "Model is not loaded."}), 500
    return jsonify(KALMAN_CHART_DATA)

@app.route("/api/performance_metrics")
def api_performance_metrics():
    if KALMAN_METRICS is None:
        return jsonify({"error": "Metrics not loaded."}), 500
    return jsonify(KALMAN_METRICS)

# --- **NEW**: Live Commodity Prices Endpoint (Yahoo Finance) ---
@app.route("/api/commodity_prices")
def api_commodity_prices():
    """
    Fetches the latest prices for the basket commodities from Yahoo Finance.
    """
    try:
        # Get the asset names from your FILE_MAP, excluding silver
        assets_to_fetch = [name for name in FILE_MAP.keys() if name != TARGET]
        # Get the corresponding Yahoo Finance tickers
        symbols = [TICKER_MAP[name] for name in assets_to_fetch]
        
        # Download data for the last 2 days to get the most recent valid price
        data = yf.download(symbols, period="2d", interval="1d")
        
        if data.empty:
            return jsonify({"error": "No data returned from yfinance"}), 500
            
        # Get the latest closing price for each
        latest_prices = data['Close'].iloc[-1]
        
        response_data = []
        for asset_name in assets_to_fetch:
            symbol = TICKER_MAP[asset_name]
            price = latest_prices.get(symbol)
            response_data.append({
                "symbol": symbol,
                "name": asset_name.capitalize(),
                # Handle cases where yfinance returns NaN (e.g., market closed)
                "price": price if price and not np.isnan(price) else 0.0
            })
            
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error fetching from yfinance: {e}")
        return jsonify({"error": str(e)}), 500


# --- Run the Server ---
if __name__ == "__main__":
    # Run all models ONCE on startup
    load_all_models()
    # Start the Flask server
    app.run(debug=True, port=5000)