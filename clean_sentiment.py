import pandas as pd
import os
import re
from pathlib import Path

def clean_stock_data(file_path):
    """
    Clean stock_data.csv (Text and Sentiment columns)
    """
    print(f"\nCleaning: {file_path}")
    
    df = pd.read_csv(file_path)
    initial_rows = len(df)
    print(f"  Initial rows: {initial_rows}")
    
    # 1. Remove duplicate rows
    df = df.drop_duplicates()
    print(f"  After removing duplicates: {len(df)} rows")
    
    # 2. Remove rows with missing Text or Sentiment
    before_na = len(df)
    df = df.dropna(subset=['Text', 'Sentiment'])
    if before_na != len(df):
        print(f"  Removed {before_na - len(df)} rows with missing Text or Sentiment")
    
    # 3. Remove rows with empty text
    before_empty = len(df)
    df = df[df['Text'].str.strip() != '']
    if before_empty != len(df):
        print(f"  Removed {before_empty - len(df)} rows with empty Text")
    
    # 4. Clean text: remove extra whitespace
    df['Text'] = df['Text'].str.strip()
    df['Text'] = df['Text'].str.replace(r'\s+', ' ', regex=True)
    
    # 5. Validate Sentiment values (should be 0 or 1)
    df['Sentiment'] = pd.to_numeric(df['Sentiment'], errors='coerce')
    before_sentiment = len(df)
    df = df[df['Sentiment'].isin([0, 1])]
    if before_sentiment != len(df):
        print(f"  Removed {before_sentiment - len(df)} rows with invalid Sentiment values")
    
    # 6. Convert Sentiment to integer
    df['Sentiment'] = df['Sentiment'].astype(int)
    
    # 7. Reset index
    df = df.reset_index(drop=True)
    
    print(f"  Final rows: {len(df)}")
    print(f"  Cleaned {initial_rows - len(df)} total rows")
    
    return df

def clean_stock_dataset(file_path):
    """
    Clean stock_dataset.csv (comprehensive dataset with technical indicators and sentiment)
    """
    print(f"\nCleaning: {file_path}")
    
    df = pd.read_csv(file_path)
    initial_rows = len(df)
    print(f"  Initial rows: {initial_rows}")
    
    # 1. Remove duplicate rows
    df = df.drop_duplicates()
    print(f"  After removing duplicates: {len(df)} rows")
    
    # 2. Convert Date to datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    before_date = len(df)
    df = df.dropna(subset=['Date'])
    if before_date != len(df):
        print(f"  Removed {before_date - len(df)} rows with invalid dates")
    
    # 3. Sort by Date
    df = df.sort_values('Date').reset_index(drop=True)
    
    # 4. Clean numeric columns
    numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'SMA_10', 'SMA_20', 
                      'EMA_10', 'RSI', 'MACD', 'Signal', 'BB_Middle', 'BB_Upper', 'BB_Lower',
                      'Sentiment_Pos', 'Sentiment_Neg', 'Sentiment_Neu', 'Sentiment_Compound']
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 5. Validate price data (High >= Low, Close between High and Low)
    invalid_mask = (df['High'] < df['Low']) | \
                   (df['Close'] > df['High']) | \
                   (df['Close'] < df['Low']) | \
                   (df['Open'] > df['High']) | \
                   (df['Open'] < df['Low'])
    
    invalid_count = invalid_mask.sum()
    if invalid_count > 0:
        print(f"  Warning: Found {invalid_count} rows with invalid price relationships")
        df = df[~invalid_mask]
    
    # 6. Validate RSI (should be between 0 and 100)
    if 'RSI' in df.columns:
        before_rsi = len(df)
        df = df[(df['RSI'] >= 0) & (df['RSI'] <= 100) | df['RSI'].isna()]
        if before_rsi != len(df):
            print(f"  Removed {before_rsi - len(df)} rows with invalid RSI values")
    
    # 7. Validate sentiment scores (should be between 0 and 1)
    sentiment_cols = ['Sentiment_Pos', 'Sentiment_Neg', 'Sentiment_Neu']
    for col in sentiment_cols:
        if col in df.columns:
            df.loc[(df[col] < 0) | (df[col] > 1), col] = None
    
    # 8. Validate Sentiment_Compound (should be between -1 and 1)
    if 'Sentiment_Compound' in df.columns:
        df.loc[(df['Sentiment_Compound'] < -1) | (df['Sentiment_Compound'] > 1), 'Sentiment_Compound'] = None
    
    # 9. Clean headline text if present
    if 'Clean_Headline' in df.columns:
        df['Clean_Headline'] = df['Clean_Headline'].fillna('')
        df['Clean_Headline'] = df['Clean_Headline'].str.strip()
        df['Clean_Headline'] = df['Clean_Headline'].str.replace(r'\s+', ' ', regex=True)
    
    # 10. Validate Target (should be 0 or 1)
    if 'Target' in df.columns:
        df['Target'] = pd.to_numeric(df['Target'], errors='coerce')
        before_target = len(df)
        df = df[df['Target'].isin([0, 1])]
        if before_target != len(df):
            print(f"  Removed {before_target - len(df)} rows with invalid Target values")
        df['Target'] = df['Target'].astype(int)
    
    # 11. Fill missing Volume with 0
    df['Volume'] = df['Volume'].fillna(0)
    
    # 12. Format Date back to string
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    
    print(f"  Final rows: {len(df)}")
    print(f"  Cleaned {initial_rows - len(df)} total rows")
    
    return df

def clean_news_data(file_path):
    """
    Clean DJIA news and NASDAQ CSV files (Label, Ticker, Headline columns)
    """
    print(f"\nCleaning: {file_path}")
    
    df = pd.read_csv(file_path)
    initial_rows = len(df)
    print(f"  Initial rows: {initial_rows}")
    
    # 1. Remove duplicate rows
    df = df.drop_duplicates()
    print(f"  After removing duplicates: {len(df)} rows")
    
    # 2. Remove rows with missing values in any column
    before_na = len(df)
    df = df.dropna(subset=['Label', 'Ticker', 'Headline'])
    if before_na != len(df):
        print(f"  Removed {before_na - len(df)} rows with missing values")
    
    # 3. Remove rows with empty headlines
    before_empty = len(df)
    df = df[df['Headline'].str.strip() != '']
    if before_empty != len(df):
        print(f"  Removed {before_empty - len(df)} rows with empty headlines")
    
    # 4. Clean headline text: remove extra whitespace
    df['Headline'] = df['Headline'].str.strip()
    df['Headline'] = df['Headline'].str.replace(r'\s+', ' ', regex=True)
    
    # 5. Clean ticker symbols: uppercase and remove whitespace
    df['Ticker'] = df['Ticker'].str.strip().str.upper()
    
    # 6. Validate Label values (should be 0 or 1)
    df['Label'] = pd.to_numeric(df['Label'], errors='coerce')
    before_label = len(df)
    df = df[df['Label'].isin([0, 1])]
    if before_label != len(df):
        print(f"  Removed {before_label - len(df)} rows with invalid Label values")
    
    # 7. Convert Label to integer
    df['Label'] = df['Label'].astype(int)
    
    # 8. Remove duplicate headlines for the same ticker
    before_dup_headlines = len(df)
    df = df.drop_duplicates(subset=['Ticker', 'Headline'])
    if before_dup_headlines != len(df):
        print(f"  Removed {before_dup_headlines - len(df)} duplicate ticker-headline combinations")
    
    # 9. Sort by Ticker and Label
    df = df.sort_values(['Ticker', 'Label']).reset_index(drop=True)
    
    print(f"  Final rows: {len(df)}")
    print(f"  Cleaned {initial_rows - len(df)} total rows")
    
    return df

def main():
    """
    Main function to clean all sentiment CSV files
    """
    base_path = r'c:\Users\viswa\GithubClonedRepos\PAML\Data\Sentiment'
    
    print("="*60)
    print("Starting Sentiment Data Cleaning Process")
    print("="*60)
    
    # Clean stock_data.csv
    stock_data_path = os.path.join(base_path, 'stock_data.csv')
    if os.path.exists(stock_data_path):
        try:
            cleaned_df = clean_stock_data(stock_data_path)
            cleaned_df.to_csv(stock_data_path, index=False)
            print(f"  ✓ Saved cleaned data to: {stock_data_path}")
        except Exception as e:
            print(f"  ✗ Error cleaning {stock_data_path}: {str(e)}")
    
    # Clean stock_dataset.csv
    stock_dataset_path = os.path.join(base_path, 'stock_dataset.csv')
    if os.path.exists(stock_dataset_path):
        try:
            cleaned_df = clean_stock_dataset(stock_dataset_path)
            cleaned_df.to_csv(stock_dataset_path, index=False)
            print(f"  ✓ Saved cleaned data to: {stock_dataset_path}")
        except Exception as e:
            print(f"  ✗ Error cleaning {stock_dataset_path}: {str(e)}")
    
    # Clean djia_news copy.csv
    djia_path = os.path.join(base_path, 'djia_news copy.csv', 'djia_news copy.csv')
    if os.path.exists(djia_path):
        try:
            cleaned_df = clean_news_data(djia_path)
            cleaned_df.to_csv(djia_path, index=False)
            print(f"  ✓ Saved cleaned data to: {djia_path}")
        except Exception as e:
            print(f"  ✗ Error cleaning {djia_path}: {str(e)}")
    
    # Clean nasdaq.csv
    nasdaq_path = os.path.join(base_path, 'nasdaq.csv', 'nasdaq.csv')
    if os.path.exists(nasdaq_path):
        try:
            cleaned_df = clean_news_data(nasdaq_path)
            cleaned_df.to_csv(nasdaq_path, index=False)
            print(f"  ✓ Saved cleaned data to: {nasdaq_path}")
        except Exception as e:
            print(f"  ✗ Error cleaning {nasdaq_path}: {str(e)}")
    
    print("\n" + "="*60)
    print("Sentiment Data Cleaning Complete!")
    print("="*60)
    print("\nSummary of cleaning operations performed:")
    print("  • Removed duplicate rows")
    print("  • Removed rows with missing critical values")
    print("  • Cleaned and normalized text data")
    print("  • Validated sentiment scores and labels (0 or 1)")
    print("  • Validated numeric ranges (RSI, sentiment scores, compound)")
    print("  • Cleaned ticker symbols (uppercase)")
    print("  • Validated price data consistency")
    print("  • Sorted data appropriately")
    print("  • Removed duplicate ticker-headline combinations")

if __name__ == "__main__":
    main()
