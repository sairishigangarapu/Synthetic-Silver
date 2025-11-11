import pandas as pd
import os
import glob
from pathlib import Path

def clean_global_markets_data(file_path):
    """
    Clean Global Stock Market CSV files
    """
    print(f"\nCleaning: {file_path}")
    
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    initial_rows = len(df)
    print(f"  Initial rows: {initial_rows}")
    
    # 1. Remove duplicate rows
    df = df.drop_duplicates()
    print(f"  After removing duplicates: {len(df)} rows")
    
    # 2. Convert Date column to datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # 3. Remove rows with invalid dates
    before_date_clean = len(df)
    df = df.dropna(subset=['Date'])
    if before_date_clean != len(df):
        print(f"  Removed {before_date_clean - len(df)} rows with invalid dates")
    
    # 4. Sort by Ticker and Date
    df = df.sort_values(['Ticker', 'Date']).reset_index(drop=True)
    
    # 5. Handle missing values in numeric columns
    numeric_columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    for col in numeric_columns:
        if col in df.columns:
            # Convert to numeric, coercing errors
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 6. Remove rows where all numeric columns are NaN
    before_numeric_clean = len(df)
    df = df.dropna(subset=['Open', 'High', 'Low', 'Close'], how='all')
    if before_numeric_clean != len(df):
        print(f"  Removed {before_numeric_clean - len(df)} rows with all missing price data")
    
    # 7. Validate price data (High >= Low, Close between High and Low)
    # Mark invalid rows
    invalid_mask = (df['High'] < df['Low']) | \
                   (df['Close'] > df['High']) | \
                   (df['Close'] < df['Low']) | \
                   (df['Open'] > df['High']) | \
                   (df['Open'] < df['Low'])
    
    invalid_count = invalid_mask.sum()
    if invalid_count > 0:
        print(f"  Warning: Found {invalid_count} rows with invalid price relationships")
        # Remove invalid rows
        df = df[~invalid_mask]
    
    # 8. Fill missing Volume with 0 (common convention)
    df['Volume'] = df['Volume'].fillna(0)
    
    # 9. Format Date back to string for consistency
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    
    print(f"  Final rows: {len(df)}")
    print(f"  Cleaned {initial_rows - len(df)} total rows")
    
    return df

def clean_sp500_data(file_path):
    """
    Clean SP 500 CSV file with quoted numbers
    """
    print(f"\nCleaning: {file_path}")
    
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    initial_rows = len(df)
    print(f"  Initial rows: {initial_rows}")
    
    # 1. Remove duplicate rows
    df = df.drop_duplicates()
    print(f"  After removing duplicates: {len(df)} rows")
    
    # 2. Convert Date column to datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # 3. Remove rows with invalid dates
    before_date_clean = len(df)
    df = df.dropna(subset=['Date'])
    if before_date_clean != len(df):
        print(f"  Removed {before_date_clean - len(df)} rows with invalid dates")
    
    # 4. Clean numeric columns (remove commas and quotes)
    numeric_columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    for col in numeric_columns:
        if col in df.columns:
            # Remove commas and convert to numeric
            if df[col].dtype == 'object':
                df[col] = df[col].str.replace(',', '').str.replace('"', '')
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 5. Sort by Date (descending to match original order)
    df = df.sort_values('Date', ascending=False).reset_index(drop=True)
    
    # 6. Remove rows where all price columns are NaN
    before_numeric_clean = len(df)
    df = df.dropna(subset=['Open', 'High', 'Low', 'Close'], how='all')
    if before_numeric_clean != len(df):
        print(f"  Removed {before_numeric_clean - len(df)} rows with all missing price data")
    
    # 7. Validate price data
    invalid_mask = (df['High'] < df['Low']) | \
                   (df['Close'] > df['High']) | \
                   (df['Close'] < df['Low']) | \
                   (df['Open'] > df['High']) | \
                   (df['Open'] < df['Low'])
    
    invalid_count = invalid_mask.sum()
    if invalid_count > 0:
        print(f"  Warning: Found {invalid_count} rows with invalid price relationships")
        df = df[~invalid_mask]
    
    # 8. Fill missing Volume with 0
    df['Volume'] = df['Volume'].fillna(0)
    
    # 9. Format Date to match original format (MMM DD, YYYY)
    df['Date'] = df['Date'].dt.strftime('%b %d, %Y')
    
    print(f"  Final rows: {len(df)}")
    print(f"  Cleaned {initial_rows - len(df)} total rows")
    
    return df

def clean_forbes_stock_data(file_path):
    """
    Clean Forbes 2000 stock market CSV files
    """
    print(f"\nCleaning: {os.path.basename(file_path)}")
    
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    initial_rows = len(df)
    print(f"  Initial rows: {initial_rows}")
    
    # 1. Remove duplicate rows
    df = df.drop_duplicates()
    duplicates_removed = initial_rows - len(df)
    if duplicates_removed > 0:
        print(f"  After removing duplicates: {len(df)} rows")
    
    # 2. Convert Date column to datetime (handle DD-MM-YYYY format)
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
    
    # 3. Remove rows with invalid dates
    before_date_clean = len(df)
    df = df.dropna(subset=['Date'])
    if before_date_clean != len(df):
        print(f"  Removed {before_date_clean - len(df)} rows with invalid dates")
    
    # 4. Sort by Date
    df = df.sort_values('Date').reset_index(drop=True)
    
    # 5. Handle missing values in numeric columns
    numeric_columns = ['Open', 'High', 'Low', 'Close', 'Adjusted Close', 'Volume']
    for col in numeric_columns:
        if col in df.columns:
            # Convert to numeric, coercing errors
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 6. Remove rows where all price columns are NaN
    before_numeric_clean = len(df)
    df = df.dropna(subset=['Open', 'High', 'Low', 'Close'], how='all')
    if before_numeric_clean != len(df):
        print(f"  Removed {before_numeric_clean - len(df)} rows with all missing price data")
    
    # 7. Validate price data (High >= Low, Close between High and Low)
    invalid_mask = (df['High'] < df['Low']) | \
                   (df['Close'] > df['High']) | \
                   (df['Close'] < df['Low']) | \
                   (df['Open'] > df['High']) | \
                   (df['Open'] < df['Low'])
    
    invalid_count = invalid_mask.sum()
    if invalid_count > 0:
        print(f"  Warning: Found {invalid_count} rows with invalid price relationships")
        # Remove invalid rows
        df = df[~invalid_mask]
    
    # 8. Fill missing Volume with 0 (common convention)
    df['Volume'] = df['Volume'].fillna(0)
    
    # 9. Fill missing Adjusted Close with Close value
    if 'Adjusted Close' in df.columns and 'Close' in df.columns:
        df['Adjusted Close'] = df['Adjusted Close'].fillna(df['Close'])
    
    # 10. Format Date back to original format (DD-MM-YYYY)
    df['Date'] = df['Date'].dt.strftime('%d-%m-%Y')
    
    if initial_rows - len(df) > 0:
        print(f"  Final rows: {len(df)} (cleaned {initial_rows - len(df)} rows)")
    
    return df

def main():
    """
    Main function to clean all CSV files in the Data directory
    """
    base_path = r'c:\Users\viswa\GithubClonedRepos\PAML\Data'
    
    print("="*60)
    print("Starting Data Cleaning Process")
    print("="*60)
    
    # Clean Global Stock Market files
    global_market_path = os.path.join(base_path, 'Global Stock market(2008-2023)')
    if os.path.exists(global_market_path):
        csv_files = glob.glob(os.path.join(global_market_path, '*.csv'))
        print(f"\nFound {len(csv_files)} Global Stock Market files")
        
        for csv_file in sorted(csv_files):
            try:
                cleaned_df = clean_global_markets_data(csv_file)
                # Save the cleaned data (overwrite original)
                cleaned_df.to_csv(csv_file, index=False)
                print(f"  ✓ Saved cleaned data to: {csv_file}")
            except Exception as e:
                print(f"  ✗ Error cleaning {csv_file}: {str(e)}")
    
    # Clean SP 500 file
    sp500_path = os.path.join(base_path, 'SP 500', 'sp 500.csv')
    if os.path.exists(sp500_path):
        try:
            cleaned_df = clean_sp500_data(sp500_path)
            # Save the cleaned data (overwrite original)
            cleaned_df.to_csv(sp500_path, index=False)
            print(f"  ✓ Saved cleaned data to: {sp500_path}")
        except Exception as e:
            print(f"  ✗ Error cleaning {sp500_path}: {str(e)}")
    
    # Clean Forbes 2000 stock market files
    forbes_path = os.path.join(base_path, 'stock_market_data', 'forbes2000', 'csv')
    if os.path.exists(forbes_path):
        csv_files = glob.glob(os.path.join(forbes_path, '*.csv'))
        print(f"\nFound {len(csv_files)} Forbes 2000 stock files")
        
        cleaned_count = 0
        error_count = 0
        
        for csv_file in sorted(csv_files):
            try:
                cleaned_df = clean_forbes_stock_data(csv_file)
                # Save the cleaned data (overwrite original)
                cleaned_df.to_csv(csv_file, index=False)
                cleaned_count += 1
            except Exception as e:
                print(f"  ✗ Error cleaning {os.path.basename(csv_file)}: {str(e)}")
                error_count += 1
        
        print(f"\n  ✓ Successfully cleaned {cleaned_count} Forbes 2000 files")
        if error_count > 0:
            print(f"  ✗ Failed to clean {error_count} files")
    
    print("\n" + "="*60)
    print("Data Cleaning Complete!")
    print("="*60)
    print("\nSummary of cleaning operations performed:")
    print("  • Removed duplicate rows")
    print("  • Converted dates to proper datetime format")
    print("  • Removed rows with invalid dates")
    print("  • Cleaned numeric columns (removed commas, quotes)")
    print("  • Validated price data consistency (High >= Low, etc.)")
    print("  • Filled missing Volume values with 0")
    print("  • Filled missing Adjusted Close with Close values")
    print("  • Sorted data appropriately")
    print("  • Removed rows with all missing price data")
    print("\nDatasets cleaned:")
    print("  • Global Stock Market (2008-2023) - 16 files")
    print("  • SP 500 index data")
    print("  • Forbes 2000 individual stock files")

if __name__ == "__main__":
    main()
