#!/usr/bin/env python3
"""
Sample script for collecting market data
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from config.settings import MARKET_DATA_DIR

def collect_stock_data(symbol: str, period: str = "1y") -> pd.DataFrame:
    """
    Collect stock data using yfinance
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'MSFT')
        period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
    
    Returns:
        DataFrame with stock data
    """
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        
        # Save to file
        output_file = MARKET_DATA_DIR / f"{symbol}_{period}_{datetime.now().strftime('%Y%m%d')}.csv"
        data.to_csv(output_file)
        print(f"Data saved to: {output_file}")
        
        return data
    except Exception as e:
        print(f"Error collecting data for {symbol}: {e}")
        return pd.DataFrame()

def main():
    """Main function"""
    print("Finance Analytics - Market Data Collection")
    print("=" * 50)
    
    # Sample stocks to collect data for
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    
    for symbol in symbols:
        print(f"\nCollecting data for {symbol}...")
        data = collect_stock_data(symbol, period="1y")
        
        if not data.empty:
            print(f"Collected {len(data)} data points")
            print(f"Date range: {data.index[0].date()} to {data.index[-1].date()}")
            print(f"Latest close: ${data['Close'].iloc[-1]:.2f}")

if __name__ == "__main__":
    main()
