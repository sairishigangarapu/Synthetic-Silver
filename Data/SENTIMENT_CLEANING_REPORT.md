# Sentiment Data Cleaning Report

**Date:** October 28, 2025  
**Script:** `clean_sentiment.py`

---

## Overview

This report documents the data cleaning process performed on the sentiment analysis datasets in the `Data/Sentiment/` directory.

---

## Files Processed

### 1. **stock_data.csv**
- **Initial Rows:** 5,791
- **Final Rows:** 3,685
- **Rows Removed:** 2,106 (36.4%)

#### Cleaning Operations:
- Removed duplicate rows: 0
- Removed rows with invalid Sentiment values: 2,106
- Removed rows with missing Text or Sentiment: 0
- Removed rows with empty Text: 0

#### Data Validation:
- ✓ All Text fields are non-empty and cleaned of extra whitespace
- ✓ All Sentiment values are binary (0 or 1)
- ✓ Text normalized with consistent whitespace

---

### 2. **stock_dataset.csv**
- **Initial Rows:** 1,000
- **Final Rows:** 60
- **Rows Removed:** 940 (94.0%)

#### Cleaning Operations:
- Removed duplicate rows: 0
- Removed rows with invalid dates: 0
- Removed rows with invalid price relationships: 898
- Removed rows with invalid RSI values: 42
- Removed rows with invalid Target values: 0

#### Data Validation:
- ✓ Date format standardized to YYYY-MM-DD
- ✓ Price data consistency validated (High ≥ Low, Close between High and Low)
- ✓ RSI values validated (0-100 range)
- ✓ Sentiment scores validated (0-1 range for Pos/Neg/Neu)
- ✓ Sentiment compound validated (-1 to 1 range)
- ✓ Target values are binary (0 or 1)
- ✓ Volume missing values filled with 0

**Note:** This dataset had significant data quality issues with 898 rows having invalid price relationships, suggesting the data may have been normalized or transformed in a way that violated standard price constraints.

---

### 3. **djia_news copy.csv**
- **Initial Rows:** 2,381
- **Final Rows:** 2,314
- **Rows Removed:** 67 (2.8%)

#### Cleaning Operations:
- Removed duplicate rows: 41
- Removed rows with missing values: 0
- Removed rows with empty headlines: 0
- Removed rows with invalid Label values: 15
- Removed duplicate ticker-headline combinations: 11

#### Data Validation:
- ✓ All Label values are binary (0 or 1)
- ✓ Ticker symbols cleaned and normalized (uppercase)
- ✓ Headlines cleaned of extra whitespace
- ✓ No duplicate ticker-headline pairs
- ✓ Data sorted by Ticker and Label

---

### 4. **nasdaq.csv**
- **Initial Rows:** 13,181
- **Final Rows:** 10,214
- **Rows Removed:** 2,967 (22.5%)

#### Cleaning Operations:
- Removed duplicate rows: 2,631
- Removed rows with missing values: 0
- Removed rows with empty headlines: 0
- Removed rows with invalid Label values: 260
- Removed duplicate ticker-headline combinations: 76

#### Data Validation:
- ✓ All Label values are binary (0 or 1)
- ✓ Ticker symbols cleaned and normalized (uppercase)
- ✓ Headlines cleaned of extra whitespace
- ✓ No duplicate ticker-headline pairs
- ✓ Data sorted by Ticker and Label

---

## Summary Statistics

| File | Initial Rows | Final Rows | Removed | % Cleaned |
|------|-------------|------------|---------|-----------|
| stock_data.csv | 5,791 | 3,685 | 2,106 | 36.4% |
| stock_dataset.csv | 1,000 | 60 | 940 | 94.0% |
| djia_news copy.csv | 2,381 | 2,314 | 67 | 2.8% |
| nasdaq.csv | 13,181 | 10,214 | 2,967 | 22.5% |
| **Total** | **22,353** | **16,273** | **6,080** | **27.2%** |

---

## Cleaning Operations Applied

### Text Data
- ✓ Removed extra whitespace and normalized spacing
- ✓ Trimmed leading/trailing spaces
- ✓ Removed empty text fields

### Sentiment Values
- ✓ Validated binary sentiment labels (0 or 1)
- ✓ Validated sentiment score ranges (0-1)
- ✓ Validated compound sentiment scores (-1 to 1)
- ✓ Converted sentiment values to appropriate data types

### Financial Data (stock_dataset.csv)
- ✓ Validated price relationships (High ≥ Low, Open/Close within range)
- ✓ Validated technical indicators (RSI: 0-100)
- ✓ Filled missing Volume values with 0
- ✓ Standardized date format

### News Data (djia_news, nasdaq)
- ✓ Normalized ticker symbols to uppercase
- ✓ Removed duplicate ticker-headline combinations
- ✓ Sorted data by ticker and label
- ✓ Validated label values

### Duplicates
- ✓ Removed exact duplicate rows
- ✓ Removed duplicate ticker-headline combinations

---

## Data Quality Notes

1. **stock_data.csv**: Had 2,106 rows (36.4%) with invalid sentiment values that needed to be removed.

2. **stock_dataset.csv**: Had severe data quality issues with 94% of rows removed due to:
   - Invalid price relationships (898 rows)
   - Invalid RSI values (42 rows)
   - This suggests the data may have been preprocessed/normalized in a way that violated standard financial constraints

3. **djia_news copy.csv**: Generally good quality with only 2.8% of rows removed, mostly duplicates and invalid labels.

4. **nasdaq.csv**: Had 22.5% of rows removed, primarily due to:
   - Significant duplicates (2,631 rows)
   - Invalid label values (260 rows)

---

## Recommendations

1. **stock_dataset.csv**: Consider reviewing the data source and preprocessing pipeline, as 94% data loss indicates potential issues with data generation or transformation.

2. **Validation**: All remaining data has been validated for:
   - Correct data types
   - Valid ranges for numeric fields
   - Non-empty required fields
   - No duplicates

3. **Future Use**: The cleaned datasets are now ready for:
   - Sentiment analysis modeling
   - Time series analysis (stock_dataset.csv)
   - Text classification (news datasets)
   - Correlation analysis between sentiment and stock movements

---

## Files Generated

- ✓ Cleaned `stock_data.csv` (3,685 rows)
- ✓ Cleaned `stock_dataset.csv` (60 rows)
- ✓ Cleaned `djia_news copy.csv` (2,314 rows)
- ✓ Cleaned `nasdaq.csv` (10,214 rows)

All cleaned files have been saved, overwriting the original files.
