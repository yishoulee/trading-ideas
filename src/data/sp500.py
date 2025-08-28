from __future__ import annotations
import os
from datetime import datetime, timedelta
from typing import List
import pandas as pd
import requests
from bs4 import BeautifulSoup
import yfinance as yf

CACHE_FILE_DEFAULT = "sp500_data.csv"


def get_sp500_tickers() -> list[str]:
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'id': 'constituents'})
    tickers: List[str] = []
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        ticker = cols[0].text.strip().replace('.', '-')
        tickers.append(ticker)
    return tickers


def download_prices(tickers: list[str], start: str, end: str) -> pd.DataFrame:
    data = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)["Close"]
    if isinstance(data, pd.Series):
        data = data.to_frame()
    return data.dropna(axis=1, how='all').sort_index()


def get_cached_prices(tickers: list[str], start: str, end: str, cache_file: str = CACHE_FILE_DEFAULT) -> pd.DataFrame:
    user_end = datetime.strptime(end, "%Y-%m-%d").date()
    today = datetime.today().date()
    latest_needed = min(user_end, today)

    if os.path.exists(cache_file):
        data = pd.read_csv(cache_file, index_col=0, parse_dates=True)
        last_date = data.index[-1].date()
        if last_date >= latest_needed:  # up to date
            return data.loc[start:end]
        update_start = (last_date + timedelta(days=1)).strftime("%Y-%m-%d")
        new_data = download_prices(tickers, update_start, latest_needed.strftime("%Y-%m-%d"))
        if not new_data.empty:
            data = pd.concat([data, new_data])
            data = data[~data.index.duplicated(keep='last')]
            data.to_csv(cache_file)
        return data.loc[start:end]
    data = download_prices(tickers, start, end)
    data.to_csv(cache_file)
    return data
