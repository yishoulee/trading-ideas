import os
import math
import sys
import pandas as pd
import numpy as np
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# -------------------- Logger Setup --------------------
class Logger(object):
    def __init__(self, filename, stream):
        self.terminal = stream
        self.log = open(filename, "w")
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self):
        self.terminal.flush()
        self.log.flush()

# Redirect stdout to both terminal and file.
sys.stdout = Logger("factor_investing_backtest_output.txt", sys.stdout)

# -------------------- Data & Caching Functions --------------------

CACHE_FILE = "sp500_data.csv"

def get_sp500_tickers():
    """
    Scrapes S&P 500 tickers from Wikipedia.
    """
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'id': 'constituents'})
    tickers = []
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        ticker = cols[0].text.strip().replace('.', '-')  # yfinance-friendly
        tickers.append(ticker)
    return tickers

def download_sp500_data(tickers, start_date, end_date):
    """
    Downloads adjusted Close price data using yfinance.
    With auto_adjust=True, the "Close" column is already adjusted.
    """
    data = yf.download(tickers, start=start_date, end=end_date, auto_adjust=True)['Close']
    data = data.dropna(axis=1, how='all').sort_index()
    return data

def get_cached_data(tickers, start_date, end_date, cache_file=CACHE_FILE):
    """
    Loads cached data if available. Only downloads new data if the cache isn’t up-to-date.
    Latest needed is the user-specified end_date (if in the past) or today.
    """
    user_end = datetime.strptime(end_date, "%Y-%m-%d").date()
    today = datetime.today().date()
    latest_needed = user_end if user_end <= today else today

    if os.path.exists(cache_file):
        print("Found cached data in", cache_file)
        data = pd.read_csv(cache_file, index_col=0, parse_dates=True)
        last_date = data.index[-1].date()
        if last_date >= latest_needed:
            print(f"Cached data is already up-to-date (last date: {last_date}).")
            return data
        else:
            update_start = last_date + timedelta(days=1)
            update_end = latest_needed.strftime("%Y-%m-%d")
            print(f"Updating cached data from {last_date} to {latest_needed}")
            new_data = yf.download(tickers, start=update_start.strftime("%Y-%m-%d"), end=update_end, auto_adjust=True)['Close']
            new_data = new_data.sort_index()
            if not new_data.empty:
                data = pd.concat([data, new_data])
                data = data[~data.index.duplicated(keep='last')]
                data.to_csv(cache_file)
            return data
    else:
        print("No cached data found. Downloading fresh data...")
        data = download_sp500_data(tickers, start_date, end_date)
        data.to_csv(cache_file)
        return data

def calculate_trailing_return(data, start_idx, end_idx):
    """
    Calculates the trailing return for each stock from start_idx to end_idx.
    """
    start_prices = data.iloc[start_idx]
    end_prices = data.iloc[end_idx]
    returns = end_prices / start_prices - 1
    return returns

# -------------------- Main Backtesting Script --------------------

# Set the backtest period.
start_date = '2018-01-01'
end_date   = '2024-12-31'

# Get the list of S&P 500 tickers.
sp500_tickers = get_sp500_tickers()
print("Retrieved", len(sp500_tickers), "tickers from S&P 500.")

# Remove known problematic tickers (e.g., 'LEN').
filtered_tickers = [t for t in sp500_tickers if t not in ['LEN']]

# Get cached (or freshly downloaded) data.
data = get_cached_data(filtered_tickers, start_date, end_date)
# Clip the data to the desired backtest period.
data = data.loc[start_date:end_date]
print("Data shape after loading and clipping:", data.shape)
if data.empty:
    raise Exception("No data available. Check your ticker list or network connection.")

# Rebalance on the first trading day of each month (MS = Month Start).
all_month_starts = data.resample('MS').first().index
# Start simulation at the first month start on or after start_date.
rebalance_dates = all_month_starts[all_month_starts >= pd.to_datetime(start_date)]

# Start capital set to $10,000.
initial_capital = 10000
portfolio_value = initial_capital
portfolio_history = []         # Overall portfolio value history.
prev_portfolio = None          # Previous composition (ticker: dollar value)

print(f"\nStarting backtest from {rebalance_dates[0].date()} to {data.index[-1].date()}")

# Backtesting loop: rebalance at the beginning of each month.
for i, rdate in enumerate(rebalance_dates):
    # Get the nearest available trading day for rdate.
    pos_array = data.index.get_indexer([rdate], method='nearest')
    if pos_array[0] == -1:
        continue
    pos = pos_array[0]
    # Ensure we have at least one day of history; if rdate is the very first day, shift one day ahead.
    if pos == 0:
        pos = 1

    # Determine the trailing period: use all available days if less than 252; otherwise use 252.
    trailing_period = pos if pos < 252 else 252
    start_period_idx = pos - trailing_period
    
    # Calculate trailing returns using the available history.
    trailing_returns = calculate_trailing_return(data, start_period_idx, pos)
    trailing_returns = trailing_returns.replace([np.inf, -np.inf], np.nan).dropna()
    if trailing_returns.empty:
        continue
    
    # Select top 10 stocks based on trailing return.
    top10 = trailing_returns.sort_values(ascending=False).head(10).index.tolist()
    
    # Determine the next rebalance date.
    if i < len(rebalance_dates) - 1:
        next_date = rebalance_dates[i+1]
    else:
        next_date = data.index[-1]
    
    # Compute target equal allocation.
    allocation = portfolio_value / len(top10)
    target_portfolio = {ticker: allocation for ticker in top10}
    
    # Compute trades compared to previous portfolio.
    trades = {}
    if prev_portfolio is None:
        # For the very first rebalance, all positions are bought.
        for ticker in top10:
            trades[ticker] = allocation
    else:
        for ticker in top10:
            prev_value = prev_portfolio.get(ticker, 0)
            trades[ticker] = allocation - prev_value
        for ticker in prev_portfolio:
            if ticker not in top10:
                trades[ticker] = -prev_portfolio[ticker]
    
    # Terminal output: show the target portfolio at the initial rebalance.
    if prev_portfolio is None:
        print(f"\nInitial Rebalance on {rdate.date()}:")
        print("Balanced Stocks and Target Allocation:")
        for ticker in target_portfolio:
            price_at_rebalance = data.iloc[pos][ticker]
            shares = allocation / price_at_rebalance
            print(f"  {ticker}: Target ${allocation:,.2f} ({shares:.2f} shares)")
    
    # Display trade details at the beginning of each month.
    print(f"\nRebalance on {rdate.date()} (effective until {next_date.date()}):")
    for ticker, trade_amt in trades.items():
        price_at_rebalance = data.iloc[pos][ticker]
        shares = abs(trade_amt) / price_at_rebalance if price_at_rebalance else 0
        action = "Buy" if trade_amt > 0 else "Sell"
        print(f"  {ticker}: {action} ${abs(trade_amt):,.2f} ({shares:.2f} shares)")
    
    # Set portfolio to the target allocation at rebalancing.
    current_portfolio = target_portfolio.copy()
    
    # Get price data for the period from rdate to next_date.
    period_data = data.loc[rdate:next_date, top10].fillna(method='ffill').dropna(axis=1)
    if period_data.empty:
        continue
    
    # Update each holding based on performance over the period.
    updated_portfolio = {}
    for ticker in current_portfolio:
        price_start = period_data.iloc[0][ticker]
        price_end = period_data.iloc[-1][ticker]
        new_value = current_portfolio[ticker] * (price_end / price_start)
        updated_portfolio[ticker] = new_value
    
    new_portfolio_value = sum(updated_portfolio.values())
    period_return = new_portfolio_value / portfolio_value - 1
    portfolio_value = new_portfolio_value
    
    portfolio_history.append({
        'date': next_date,
        'portfolio_value': portfolio_value,
        'period_return': period_return
    })
    
    # Terminal output: show updated portfolio composition.
    print("Updated Portfolio Composition:")
    for ticker, value in updated_portfolio.items():
        print(f"  {ticker}: ${value:,.2f}")
    print(f"Total Portfolio Value: ${portfolio_value:,.2f}\n")
    
    # Set previous portfolio for next iteration.
    prev_portfolio = updated_portfolio.copy()

# Plot overall portfolio value evolution.
portfolio_df = pd.DataFrame(portfolio_history)
portfolio_df.set_index('date', inplace=True)

plt.figure(figsize=(12, 6))
plt.plot(portfolio_df.index, portfolio_df['portfolio_value'], marker='o', label='Portfolio Value')
plt.title("Backtest: Portfolio Value Over Time")
plt.xlabel("Date")
plt.ylabel("Portfolio Value ($)")
plt.legend()
plt.grid(True)
plt.show()

print(f"\nInitial Capital: ${initial_capital:,.2f}")
print(f"Final Portfolio Value: ${portfolio_value:,.2f}")
print(f"Total Return: {(portfolio_value/initial_capital - 1):.2%}")
