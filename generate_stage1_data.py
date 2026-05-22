import argparse
from pathlib import Path
import numpy as np
import pandas as pd


def simulate_stock_series(dates, start_price, drift, vol, seed=None):
    rng = np.random.default_rng(seed)
    n = len(dates)
    returns = rng.normal(loc=drift / 252, scale=vol / np.sqrt(252), size=n)
    prices = start_price * np.exp(np.cumsum(returns))
    return prices, returns


def build_ohlcv(prices, returns):
    opens = np.concatenate([[prices[0]], prices[:-1]])
    closes = prices
    highs = np.maximum(opens, closes) * (1 + np.abs(np.random.normal(scale=0.005, size=len(prices))))
    lows = np.minimum(opens, closes) * (1 - np.abs(np.random.normal(scale=0.005, size=len(prices))))
    volume = np.round(np.maximum(100_000, np.random.lognormal(mean=11, sigma=0.5, size=len(prices)))).astype(int)
    df = pd.DataFrame({
        'Date': prices.index,
        'Open': opens,
        'High': highs,
        'Low': lows,
        'Close': closes,
        'Volume': volume,
    })
    return df


def generate_stage1_data(output_dir: Path, n_tickers: int = 100, start_date: str = '2010-01-01', end_date: str = '2026-04-10'):
    output_dir.mkdir(parents=True, exist_ok=True)

    dates = pd.date_range(start=start_date, end=end_date, freq='B')
    if dates.empty:
        raise ValueError('Date range produced no business days')

    # Simulate market index (SPY) first
    spy_prices, spy_returns = simulate_stock_series(dates, start_price=100.0, drift=0.07, vol=0.18, seed=42)
    spy = pd.Series(spy_prices, index=dates, name='SPY')
    spy_df = pd.DataFrame({'Date': dates, 'Open': spy.shift(1).fillna(spy.iloc[0]), 'High': spy * 1.0025, 'Low': spy * 0.9975, 'Close': spy, 'Volume': 20_000_000})
    spy_df.to_csv(output_dir / 'SPY.csv', index=False)

    tickers = [f'TICKER{i:03d}' for i in range(n_tickers)]
    for idx, ticker in enumerate(tickers):
        sector_factor = 0.8 + 0.4 * (idx % 5) / 4
        beta = 0.8 + 0.4 * ((idx % 7) / 6)
        stock_returns = beta * spy_returns + np.random.default_rng(1000 + idx).normal(loc=0.0, scale=0.01, size=len(dates))
        stock_prices = 20 + np.cumsum(stock_returns * 20)
        stock_prices = np.maximum(1.0, stock_prices)
        stock_prices = stock_prices * (1 + 0.1 * np.sin(np.linspace(0, 8 * np.pi, len(dates)) + idx))
        stock = pd.Series(stock_prices, index=dates).replace([np.inf, -np.inf], np.nan)
        stock = stock.ffill().bfill()

        opens = stock.shift(1).fillna(stock.iloc[0])
        closes = stock
        highs = np.maximum(opens, closes) * (1 + np.abs(np.random.normal(scale=0.006, size=len(stock))))
        lows = np.minimum(opens, closes) * (1 - np.abs(np.random.normal(scale=0.006, size=len(stock))))
        volume = np.round(np.maximum(50_000, np.random.lognormal(mean=10.5, sigma=0.7, size=len(stock)))).astype(int)

        df = pd.DataFrame({
            'Date': dates,
            'Open': opens,
            'High': highs,
            'Low': lows,
            'Close': closes,
            'Volume': volume,
        })
        df.to_csv(output_dir / f'{ticker}.csv', index=False)

    print(f'Generated {len(tickers) + 1} OHLCV CSV files in {output_dir}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate synthetic Stage 1 S&P 100 OHLCV dataset')
    parser.add_argument('--output', type=Path, default=Path('Stage 1 data layer/Universe_stock data'),
                        help='Output directory for generated stock CSV files')
    parser.add_argument('--tickers', type=int, default=100, help='Number of synthetic S&P 100 tickers (excluding SPY)')
    parser.add_argument('--start-date', default='2010-01-01', help='Start date for generated data')
    parser.add_argument('--end-date', default='2026-04-10', help='End date for generated data')
    args = parser.parse_args()

    generate_stage1_data(args.output, n_tickers=args.tickers, start_date=args.start_date, end_date=args.end_date)
