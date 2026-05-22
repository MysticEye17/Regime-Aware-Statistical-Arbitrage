import time
from pathlib import Path
import pandas as pd
import requests
from bs4 import BeautifulSoup
import yfinance as yf

WIKI_URL = 'https://en.wikipedia.org/wiki/S%26P_100'
OUTPUT_DIR = Path(r'C:\Arbion Research\Stage 1 data layer\Universe_stock data')
START_DATE = '2013-01-01'
END_DATE = '2025-12-31'


def fetch_sp100_tickers():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    resp = requests.get(WIKI_URL, headers=headers, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'lxml')
    table = soup.find_all('table', {'class': 'wikitable'})[1]
    rows = table.find_all('tr')[1:]
    tickers = [row.find_all('td')[0].text.strip() for row in rows if row.find_all('td')]
    return [t for t in tickers if t]


def download_ticker(ticker):
    yahoo_ticker = ticker.replace('.', '-')
    print(f'Downloading {ticker} as {yahoo_ticker}...')
    data = yf.download(yahoo_ticker, start=START_DATE, end=END_DATE, progress=False, threads=False)
    if data.empty:
        raise ValueError(f'No data for {ticker} ({yahoo_ticker})')
    if isinstance(data.columns, pd.MultiIndex):
        data = data.loc[:, (['Open', 'High', 'Low', 'Close', 'Volume'], slice(None))]
        data.columns = data.columns.get_level_values(0)
    else:
        data = data[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    data.reset_index(inplace=True)
    out_path = OUTPUT_DIR / f'{ticker}.csv'
    data.to_csv(out_path, index=False)
    print(f'  saved {out_path} ({len(data)} rows)')
    return out_path


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    tickers = fetch_sp100_tickers()
    tickers = ['SPY'] + tickers
    print(f'Found {len(tickers)} tickers to download')

    for ticker in tickers:
        out_path = OUTPUT_DIR / f'{ticker}.csv'
        if out_path.exists():
            print(f'Skipping {ticker}: already downloaded')
            continue
        attempts = 0
        while attempts < 5:
            try:
                download_ticker(ticker)
                break
            except Exception as exc:
                attempts += 1
                print(f'  failed {ticker} attempt {attempts}: {exc}')
                if attempts >= 5:
                    raise
                time.sleep(10)

    print('Download complete.')


if __name__ == '__main__':
    main()
