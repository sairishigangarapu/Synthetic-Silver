import pandas as pd
import os
import numpy as np
from pathlib import Path

def clean_commodity_2000_2022(file_path):
    """
    Clean commodity 2000-2022.csv (Symbol, Date, OHLCV format)
    """
    print(f"\nCleaning: {os.path.basename(file_path)}")
    
    df = pd.read_csv(file_path)
    initial_rows = len(df)
    print(f"  Initial rows: {initial_rows}")
    
    # 1. Remove duplicate rows
    df = df.drop_duplicates()
    duplicates_removed = initial_rows - len(df)
    if duplicates_removed > 0:
        print(f"  After removing duplicates: {len(df)} rows")
    
    # 2. Convert Date column to datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # 3. Remove rows with invalid dates
    before_date_clean = len(df)
    df = df.dropna(subset=['Date'])
    if before_date_clean != len(df):
        print(f"  Removed {before_date_clean - len(df)} rows with invalid dates")
    
    # 4. Clean Symbol column
    df['Symbol'] = df['Symbol'].str.strip().str.title()
    
    # 5. Sort by Symbol and Date
    df = df.sort_values(['Symbol', 'Date']).reset_index(drop=True)
    
    # 6. Handle missing values in numeric columns
    numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 7. Remove rows where all price columns are NaN
    before_numeric_clean = len(df)
    df = df.dropna(subset=['Open', 'High', 'Low', 'Close'], how='all')
    if before_numeric_clean != len(df):
        print(f"  Removed {before_numeric_clean - len(df)} rows with all missing price data")
    
    # 8. Validate price data (High >= Low, Close between High and Low)
    invalid_mask = (df['High'] < df['Low']) | \
                   (df['Close'] > df['High']) | \
                   (df['Close'] < df['Low']) | \
                   (df['Open'] > df['High']) | \
                   (df['Open'] < df['Low'])
    
    invalid_count = invalid_mask.sum()
    if invalid_count > 0:
        print(f"  Warning: Found {invalid_count} rows with invalid price relationships")
        df = df[~invalid_mask]
    
    # 9. Fill missing Volume with 0
    df['Volume'] = df['Volume'].fillna(0)
    
    # 10. Remove duplicate Symbol-Date combinations (keep first)
    before_dup = len(df)
    df = df.drop_duplicates(subset=['Symbol', 'Date'], keep='first')
    if before_dup != len(df):
        print(f"  Removed {before_dup - len(df)} duplicate Symbol-Date combinations")
    
    # 11. Format Date back to string
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    
    if initial_rows - len(df) > 0:
        print(f"  Final rows: {len(df)} (cleaned {initial_rows - len(df)} rows)")
    else:
        print(f"  Final rows: {len(df)}")
    
    return df

def clean_commodity_futures(file_path):
    """
    Clean commodity_futures.csv (wide format with multiple commodity columns)
    """
    print(f"\nCleaning: {os.path.basename(file_path)}")
    
    df = pd.read_csv(file_path)
    initial_rows = len(df)
    print(f"  Initial rows: {initial_rows}")
    
    # 1. Remove duplicate rows
    df = df.drop_duplicates()
    duplicates_removed = initial_rows - len(df)
    if duplicates_removed > 0:
        print(f"  After removing duplicates: {len(df)} rows")
    
    # 2. Convert Date column to datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # 3. Remove rows with invalid dates
    before_date_clean = len(df)
    df = df.dropna(subset=['Date'])
    if before_date_clean != len(df):
        print(f"  Removed {before_date_clean - len(df)} rows with invalid dates")
    
    # 4. Sort by Date
    df = df.sort_values('Date').reset_index(drop=True)
    
    # 5. Convert all commodity columns to numeric
    commodity_columns = [col for col in df.columns if col != 'Date']
    for col in commodity_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 6. Remove rows where all commodity values are NaN
    before_all_nan = len(df)
    df = df.dropna(subset=commodity_columns, how='all')
    if before_all_nan != len(df):
        print(f"  Removed {before_all_nan - len(df)} rows with all missing commodity data")
    
    # 7. Remove duplicate dates (keep first)
    before_dup = len(df)
    df = df.drop_duplicates(subset=['Date'], keep='first')
    if before_dup != len(df):
        print(f"  Removed {before_dup - len(df)} duplicate dates")
    
    # 8. Format Date back to string
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    
    if initial_rows - len(df) > 0:
        print(f"  Final rows: {len(df)} (cleaned {initial_rows - len(df)} rows)")
    else:
        print(f"  Final rows: {len(df)}")
    
    return df

def clean_silver_historical_data(file_path):
    """
    Clean Silver Historical Data.csv with commas and percentage formats
    """
    print(f"\nCleaning: {os.path.basename(file_path)}")
    
    df = pd.read_csv(file_path)
    initial_rows = len(df)
    print(f"  Initial rows: {initial_rows}")
    
    # 1. Remove duplicate rows
    df = df.drop_duplicates()
    duplicates_removed = initial_rows - len(df)
    if duplicates_removed > 0:
        print(f"  After removing duplicates: {len(df)} rows")
    
    # 2. Convert Date column to datetime (DD-MM-YYYY format)
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
    
    # 3. Remove rows with invalid dates
    before_date_clean = len(df)
    df = df.dropna(subset=['Date'])
    if before_date_clean != len(df):
        print(f"  Removed {before_date_clean - len(df)} rows with invalid dates")
    
    # 4. Sort by Date
    df = df.sort_values('Date').reset_index(drop=True)
    
    # 5. Clean numeric columns (remove commas)
    numeric_columns = ['Price', 'Open', 'High', 'Low']
    for col in numeric_columns:
        if col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].str.replace(',', '')
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 6. Clean Volume column (remove 'K', 'M' suffixes and convert)
    if 'Vol.' in df.columns:
        df['Vol.'] = df['Vol.'].astype(str).str.replace('K', '').str.replace('M', '').str.replace('-', '0')
        df['Vol.'] = pd.to_numeric(df['Vol.'], errors='coerce')
        # Convert K (thousands) - assuming values < 1000 are in K
        df.loc[df['Vol.'] < 1000, 'Vol.'] = df.loc[df['Vol.'] < 1000, 'Vol.'] * 1000
        df['Vol.'] = df['Vol.'].fillna(0)
    
    # 7. Clean Change % column (remove % sign)
    if 'Change %' in df.columns:
        df['Change %'] = df['Change %'].astype(str).str.replace('%', '').str.replace(',', '')
        df['Change %'] = pd.to_numeric(df['Change %'], errors='coerce')
    
    # 8. Remove rows where all price columns are NaN
    before_numeric_clean = len(df)
    df = df.dropna(subset=['Price', 'Open', 'High', 'Low'], how='all')
    if before_numeric_clean != len(df):
        print(f"  Removed {before_numeric_clean - len(df)} rows with all missing price data")
    
    # 9. Validate price data
    invalid_mask = (df['High'] < df['Low']) | \
                   (df['Price'] > df['High']) | \
                   (df['Price'] < df['Low']) | \
                   (df['Open'] > df['High']) | \
                   (df['Open'] < df['Low'])
    
    invalid_count = invalid_mask.sum()
    if invalid_count > 0:
        print(f"  Warning: Found {invalid_count} rows with invalid price relationships")
        df = df[~invalid_mask]
    
    # 10. Remove duplicate dates (keep first)
    before_dup = len(df)
    df = df.drop_duplicates(subset=['Date'], keep='first')
    if before_dup != len(df):
        print(f"  Removed {before_dup - len(df)} duplicate dates")
    
    # 11. Format Date back to original format
    df['Date'] = df['Date'].dt.strftime('%d-%m-%Y')
    
    if initial_rows - len(df) > 0:
        print(f"  Final rows: {len(df)} (cleaned {initial_rows - len(df)} rows)")
    else:
        print(f"  Final rows: {len(df)}")
    
    return df

def clean_lbma_silver(file_path):
    """
    Clean LBMA-SILVER.csv (London Bullion Market Association silver prices)
    """
    print(f"\nCleaning: {os.path.basename(file_path)}")
    
    df = pd.read_csv(file_path)
    initial_rows = len(df)
    print(f"  Initial rows: {initial_rows}")
    
    # 1. Remove duplicate rows
    df = df.drop_duplicates()
    duplicates_removed = initial_rows - len(df)
    if duplicates_removed > 0:
        print(f"  After removing duplicates: {len(df)} rows")
    
    # 2. Convert Date column to datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # 3. Remove rows with invalid dates
    before_date_clean = len(df)
    df = df.dropna(subset=['Date'])
    if before_date_clean != len(df):
        print(f"  Removed {before_date_clean - len(df)} rows with invalid dates")
    
    # 4. Sort by Date
    df = df.sort_values('Date').reset_index(drop=True)
    
    # 5. Convert price columns to numeric
    price_columns = ['USD', 'GBP', 'EURO']
    for col in price_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 6. Remove rows where all price columns are NaN
    before_numeric_clean = len(df)
    df = df.dropna(subset=price_columns, how='all')
    if before_numeric_clean != len(df):
        print(f"  Removed {before_numeric_clean - len(df)} rows with all missing price data")
    
    # 7. Validate prices (should be positive)
    for col in price_columns:
        if col in df.columns:
            before_negative = len(df)
            df = df[df[col] > 0]
            if before_negative != len(df):
                print(f"  Removed {before_negative - len(df)} rows with negative {col} prices")
    
    # 8. Remove duplicate dates (keep first)
    before_dup = len(df)
    df = df.drop_duplicates(subset=['Date'], keep='first')
    if before_dup != len(df):
        print(f"  Removed {before_dup - len(df)} duplicate dates")
    
    # 9. Format Date back to string
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    
    if initial_rows - len(df) > 0:
        print(f"  Final rows: {len(df)} (cleaned {initial_rows - len(df)} rows)")
    else:
        print(f"  Final rows: {len(df)}")
    
    return df

def clean_silver_simple(file_path):
    """
    Clean Silver.csv and similar simple format files
    """
    print(f"\nCleaning: {os.path.basename(file_path)}")
    
    df = pd.read_csv(file_path)
    initial_rows = len(df)
    print(f"  Initial rows: {initial_rows}")
    
    # 1. Remove duplicate rows
    df = df.drop_duplicates()
    duplicates_removed = initial_rows - len(df)
    if duplicates_removed > 0:
        print(f"  After removing duplicates: {len(df)} rows")
    
    # 2. Convert Date column to datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # 3. Remove rows with invalid dates
    before_date_clean = len(df)
    df = df.dropna(subset=['Date'])
    if before_date_clean != len(df):
        print(f"  Removed {before_date_clean - len(df)} rows with invalid dates")
    
    # 4. Sort by Date
    df = df.sort_values('Date').reset_index(drop=True)
    
    # 5. Convert numeric columns
    numeric_columns = [col for col in df.columns if col != 'Date']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 6. Validate price data if OHLC columns exist
    if all(col in df.columns for col in ['Open', 'High', 'Low', 'Price']):
        invalid_mask = (df['High'] < df['Low']) | \
                       (df['Price'] > df['High']) | \
                       (df['Price'] < df['Low']) | \
                       (df['Open'] > df['High']) | \
                       (df['Open'] < df['Low'])
        
        invalid_count = invalid_mask.sum()
        if invalid_count > 0:
            print(f"  Warning: Found {invalid_count} rows with invalid price relationships")
            df = df[~invalid_mask]
    
    # 7. Remove rows where all numeric columns are NaN
    before_numeric_clean = len(df)
    df = df.dropna(subset=numeric_columns, how='all')
    if before_numeric_clean != len(df):
        print(f"  Removed {before_numeric_clean - len(df)} rows with all missing data")
    
    # 8. Remove duplicate dates (keep first)
    before_dup = len(df)
    df = df.drop_duplicates(subset=['Date'], keep='first')
    if before_dup != len(df):
        print(f"  Removed {before_dup - len(df)} duplicate dates")
    
    # 9. Format Date back to string
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    
    if initial_rows - len(df) > 0:
        print(f"  Final rows: {len(df)} (cleaned {initial_rows - len(df)} rows)")
    else:
        print(f"  Final rows: {len(df)}")
    
    return df

def clean_silver_price(file_path):
    """
    Clean silver_price.csv (simple date-price format)
    """
    print(f"\nCleaning: {os.path.basename(file_path)}")
    
    df = pd.read_csv(file_path)
    initial_rows = len(df)
    print(f"  Initial rows: {initial_rows}")
    
    # 1. Remove duplicate rows
    df = df.drop_duplicates()
    duplicates_removed = initial_rows - len(df)
    if duplicates_removed > 0:
        print(f"  After removing duplicates: {len(df)} rows")
    
    # 2. Convert date column to datetime (handle lowercase 'date')
    date_col = 'date' if 'date' in df.columns else 'Date'
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    
    # 3. Remove rows with invalid dates
    before_date_clean = len(df)
    df = df.dropna(subset=[date_col])
    if before_date_clean != len(df):
        print(f"  Removed {before_date_clean - len(df)} rows with invalid dates")
    
    # 4. Sort by date
    df = df.sort_values(date_col).reset_index(drop=True)
    
    # 5. Convert price to numeric
    price_col = 'price' if 'price' in df.columns else 'Price'
    df[price_col] = pd.to_numeric(df[price_col], errors='coerce')
    
    # 6. Remove rows with missing prices
    before_price_clean = len(df)
    df = df.dropna(subset=[price_col])
    if before_price_clean != len(df):
        print(f"  Removed {before_price_clean - len(df)} rows with missing prices")
    
    # 7. Validate prices (should be positive)
    before_negative = len(df)
    df = df[df[price_col] > 0]
    if before_negative != len(df):
        print(f"  Removed {before_negative - len(df)} rows with negative/zero prices")
    
    # 8. Remove duplicate dates (keep first)
    before_dup = len(df)
    df = df.drop_duplicates(subset=[date_col], keep='first')
    if before_dup != len(df):
        print(f"  Removed {before_dup - len(df)} duplicate dates")
    
    # 9. Format date back to string
    df[date_col] = df[date_col].dt.strftime('%Y-%m-%d')
    
    if initial_rows - len(df) > 0:
        print(f"  Final rows: {len(df)} (cleaned {initial_rows - len(df)} rows)")
    else:
        print(f"  Final rows: {len(df)}")
    
    return df

def main():
    """
    Main function to clean all commodities and silver CSV files
    """
    base_path = r'c:\Users\viswa\GithubClonedRepos\PAML\Data'
    
    print("="*60)
    print("Starting Commodities and Silver Data Cleaning Process")
    print("="*60)
    
    files_cleaned = 0
    files_failed = 0
    
    # Clean commodity 2000-2022.csv
    commodity_2000_path = os.path.join(base_path, 'Commodities', 'commodity 2000-2022.csv')
    if os.path.exists(commodity_2000_path):
        try:
            cleaned_df = clean_commodity_2000_2022(commodity_2000_path)
            cleaned_df.to_csv(commodity_2000_path, index=False)
            print(f"  ✓ Saved cleaned data")
            files_cleaned += 1
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            files_failed += 1
    
    # Clean commodity_futures.csv
    futures_path = os.path.join(base_path, 'Commodities', 'commodity_futures.csv')
    if os.path.exists(futures_path):
        try:
            cleaned_df = clean_commodity_futures(futures_path)
            cleaned_df.to_csv(futures_path, index=False)
            print(f"  ✓ Saved cleaned data")
            files_cleaned += 1
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            files_failed += 1
    
    # Clean Silver Historical Data.csv
    silver_historical_path = os.path.join(base_path, 'Commodities', 'Silver Historical Data.csv')
    if os.path.exists(silver_historical_path):
        try:
            cleaned_df = clean_silver_historical_data(silver_historical_path)
            cleaned_df.to_csv(silver_historical_path, index=False)
            print(f"  ✓ Saved cleaned data")
            files_cleaned += 1
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            files_failed += 1
    
    # Clean LBMA-SILVER.csv
    lbma_path = os.path.join(base_path, 'Silver', 'LBMA-SILVER.csv')
    if os.path.exists(lbma_path):
        try:
            cleaned_df = clean_lbma_silver(lbma_path)
            cleaned_df.to_csv(lbma_path, index=False)
            print(f"  ✓ Saved cleaned data")
            files_cleaned += 1
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            files_failed += 1
    
    # Clean Silver.csv
    silver_path = os.path.join(base_path, 'Silver', 'Silver.csv')
    if os.path.exists(silver_path):
        try:
            cleaned_df = clean_silver_simple(silver_path)
            cleaned_df.to_csv(silver_path, index=False)
            print(f"  ✓ Saved cleaned data")
            files_cleaned += 1
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            files_failed += 1
    
    # Clean silver_price.csv
    silver_price_path = os.path.join(base_path, 'Silver', 'silver_price.csv')
    if os.path.exists(silver_price_path):
        try:
            cleaned_df = clean_silver_price(silver_price_path)
            cleaned_df.to_csv(silver_price_path, index=False)
            print(f"  ✓ Saved cleaned data")
            files_cleaned += 1
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            files_failed += 1
    
    # Clean other metal historical data files (same format as Silver Historical Data)
    metal_files = [
        'Aluminium Historical Data.csv',
        'Copper Historical Data.csv',
        'Lead Historical Data.csv',
        'Nickel Historical Data.csv',
        'Refined Gold Historical Data.csv',
        'Zinc Historical Data.csv'
    ]
    
    for metal_file in metal_files:
        metal_path = os.path.join(base_path, 'Commodities', metal_file)
        if os.path.exists(metal_path):
            try:
                cleaned_df = clean_silver_historical_data(metal_path)
                cleaned_df.to_csv(metal_path, index=False)
                print(f"  ✓ Saved cleaned data")
                files_cleaned += 1
            except Exception as e:
                print(f"  ✗ Error: {str(e)}")
                files_failed += 1
    
    print("\n" + "="*60)
    print("Commodities and Silver Data Cleaning Complete!")
    print("="*60)
    print(f"\n✓ Successfully cleaned: {files_cleaned} files")
    if files_failed > 0:
        print(f"✗ Failed to clean: {files_failed} files")
    
    print("\nSummary of cleaning operations performed:")
    print("  • Removed duplicate rows and duplicate dates")
    print("  • Converted dates to proper datetime format")
    print("  • Removed rows with invalid dates")
    print("  • Cleaned numeric columns (removed commas, K/M suffixes)")
    print("  • Validated price data consistency (High >= Low, etc.)")
    print("  • Removed rows with all missing data")
    print("  • Sorted data by date")
    print("  • Standardized date formats")
    print("\nDatasets cleaned:")
    print("  • Commodities:")
    print("    - commodity 2000-2022.csv (multi-commodity OHLCV)")
    print("    - commodity_futures.csv (24 commodity futures)")
    print("    - Silver Historical Data.csv")
    print("    - Aluminium Historical Data.csv")
    print("    - Copper Historical Data.csv")
    print("    - Lead Historical Data.csv")
    print("    - Nickel Historical Data.csv")
    print("    - Refined Gold Historical Data.csv")
    print("    - Zinc Historical Data.csv")
    print("  • Silver:")
    print("    - LBMA-SILVER.csv (USD, GBP, EURO)")
    print("    - Silver.csv (OHLC)")
    print("    - silver_price.csv (historical)")

if __name__ == "__main__":
    main()
