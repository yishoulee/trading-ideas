# SP500-Factor-Investing-Backtest-Engine

This project implements a backtesting framework for a factor-based investing strategy that selects stocks from the S&P 500 based on their trailing returns. The goal is to simulate a monthly rebalancing strategy that targets the top 10 performers, tracking portfolio evolution over time.

---

## Overview

- **Strategy:** At each month’s start, the strategy calculates the trailing returns (using up to 252 trading days of history) for all S&P 500 stocks. It then selects the top 10 stocks by performance and rebalances the portfolio to assign equal weights to each.
- **Data Sources:** 
  - **S&P 500 Tickers:** Scraped from Wikipedia.
  - **Stock Data:** Downloaded from Yahoo Finance via the `yfinance` library.
- **Output:** The code logs detailed transactions and portfolio updates to a file and displays a plot of the portfolio value evolution.

---

## Features

- **Logging:** Captures console output to both the terminal and a log file (`factor_investing_backtest_output.txt`).
- **Data Caching:** Saves downloaded S&P 500 historical data to `sp500_data.csv` to avoid redundant downloads.
- **Monthly Rebalancing:** Uses the first trading day of each month for rebalancing.
- **Dynamic Trailing Return Calculation:** Adjusts the trailing window based on available data (up to 252 trading days).
- **Visualization:** Plots the portfolio's value over time using matplotlib.

---

## Dependencies

Ensure you have Python 3 installed along with the following libraries:

- [pandas](https://pandas.pydata.org/)
- [numpy](https://numpy.org/)
- [yfinance](https://pypi.org/project/yfinance/)
- [requests](https://docs.python-requests.org/)
- [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [lxml](https://lxml.de/)
- [matplotlib](https://matplotlib.org/)

You can install the required libraries using pip:

```bash
pip install pandas numpy yfinance requests beautifulsoup4 lxml matplotlib
```

---

## Code Structure

### 1. Logger Setup
- **Purpose:** Redirects standard output to both the terminal and a log file.
- **Implementation:** The `Logger` class writes messages to both `sys.stdout` and a file named `factor_investing_backtest_output.txt`.

### 2. Data & Caching Functions

- **`get_sp500_tickers()`**
  - **Function:** Scrapes the list of S&P 500 tickers from Wikipedia.
  - **Details:** Processes the table from the Wikipedia page to extract and format tickers for compatibility with yfinance.

- **`download_sp500_data()`**
  - **Function:** Downloads historical adjusted closing price data for the provided tickers using yfinance.
  - **Details:** Retrieves data over the specified date range and cleans it by dropping columns with no data.

- **`get_cached_data()`**
  - **Function:** Checks if a cache file (`sp500_data.csv`) exists and is up-to-date. If not, downloads and updates the cached data.
  - **Details:** Ensures efficient data usage by updating only the missing portions of the dataset.

- **`calculate_trailing_return()`**
  - **Function:** Computes the trailing return for each stock over a given period.
  - **Details:** Calculates returns based on start and end prices from the historical data.

### 3. Main Backtesting Script

- **Backtest Period:** Configured to run from `2018-01-01` to `2024-12-31`.
- **Ticker Filtering:** Retrieves and filters the list of S&P 500 tickers to remove problematic entries.
- **Data Preparation:** Loads and clips the historical data to the backtest period.
- **Monthly Rebalancing:**
  - **Rebalance Dates:** Uses the first trading day of each month.
  - **Strategy Execution:** 
    - Calculates trailing returns for each stock.
    - Selects the top 10 stocks by performance.
    - Allocates the portfolio equally among these stocks.
    - Logs the trades required to adjust the portfolio from the previous period.
- **Portfolio Updates:** 
  - Simulates the performance of the portfolio over each period.
  - Updates the overall portfolio value and records period returns.
- **Visualization:** Uses matplotlib to plot the evolution of the portfolio value over time.

---

## Running the Code

1. **Save the Code:**
   - Save the complete script to a file, for example, `backtest.py`.

2. **Execute the Script:**
   ```bash
   python backtest.py
   ```

3. **Outputs:**
   - **Log File:** Detailed execution logs will be saved in `factor_investing_backtest_output.txt`.
   - **Data Cache:** Historical stock data will be stored in `sp500_data.csv`.
   - **Plot:** A window displaying the portfolio value evolution over time.
   - **Console Output:** Final portfolio value and total return printed in the terminal.

---

## Customization

- **Backtest Period:** Modify the `start_date` and `end_date` variables to test different time ranges.
- **Strategy Parameters:** Change the number of stocks selected (currently 10) or adjust the trailing period used for return calculations.
- **Data Refresh:** To force a data refresh, delete the `sp500_data.csv` file and re-run the script.
