# data_manager.py - Efficient Data Management for Portfolio Analysis
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os
import pickle
import time
import warnings
from pathlib import Path
warnings.filterwarnings('ignore')

class DataManager:
    """
    Efficient data manager for handling yfinance data fetching with caching and rate limiting.
    """
    
    def __init__(self, cache_dir="data/cache", max_cache_age_days=7, rate_limit_delay=0.2):
        """
        Initialize data manager.
        
        Args:
            cache_dir (str): Directory to store cached data
            max_cache_age_days (int): Maximum age of cached data in days
            rate_limit_delay (float): Delay between API calls in seconds
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_cache_age = timedelta(days=max_cache_age_days)
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0
        
    def _get_cache_path(self, tickers, time_period):
        """Generate cache file path for given tickers and time period."""
        ticker_str = "_".join(sorted(tickers))
        return self.cache_dir / f"{ticker_str}_{time_period}y.pkl"
    
    def _is_cache_valid(self, cache_path):
        """Check if cached data is still valid."""
        if not cache_path.exists():
            return False
        
        # Check file age
        file_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
        return file_age < self.max_cache_age
    
    def _load_from_cache(self, cache_path):
        """Load data from cache."""
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Warning: Failed to load cache: {e}")
            return None
    
    def _save_to_cache(self, cache_path, data):
        """Save data to cache."""
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"Warning: Failed to save cache: {e}")
    
    def _rate_limit(self):
        """Implement rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    def fetch_data(self, tickers, time_period=2, force_refresh=False):
        """
        Fetch data efficiently with caching and rate limiting.
        
        Args:
            tickers (list): List of stock tickers
            time_period (int): Number of years of data to fetch
            force_refresh (bool): Force refresh even if cache exists
            
        Returns:
            pandas.DataFrame: Returns data
        """
        # Check cache first
        cache_path = self._get_cache_path(tickers, time_period)
        
        if not force_refresh and self._is_cache_valid(cache_path):
            cached_data = self._load_from_cache(cache_path)
            if cached_data is not None:
                print(f"Using cached data for {len(tickers)} tickers ({time_period} years)")
                return cached_data
        
        # Fetch fresh data with rate limiting
        print(f"Fetching fresh data for {len(tickers)} tickers ({time_period} years)")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=time_period * 365)
        
        # Fetch data with rate limiting
        self._rate_limit()
        
        try:
            # Download data with minimal progress output
            data = yf.download(
                tickers, 
                start=start_date, 
                end=end_date, 
                progress=False,
                threads=False  # Disable threading to avoid rate limits
            )
            
            if data.empty:
                raise Exception("No data available for the specified tickers")
            
            # Use adjusted close prices
            if 'Adj Close' in data.columns:
                prices = data['Adj Close']
            else:
                prices = data['Close']
            
            # Calculate returns
            returns = prices.pct_change().dropna()
            
            # Cache the data
            self._save_to_cache(cache_path, returns)
            
            return returns
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            # Try to load from cache even if expired
            cached_data = self._load_from_cache(cache_path)
            if cached_data is not None:
                print("Using expired cache data as fallback")
                return cached_data
            raise
    
    def fetch_data_batch(self, ticker_groups, time_period=2):
        """
        Fetch data for multiple groups of tickers efficiently.
        
        Args:
            ticker_groups (list): List of ticker lists
            time_period (int): Number of years of data to fetch
            
        Returns:
            dict: Dictionary mapping ticker groups to their data
        """
        results = {}
        
        for i, tickers in enumerate(ticker_groups):
            print(f"Processing group {i+1}/{len(ticker_groups)}: {tickers}")
            try:
                data = self.fetch_data(tickers, time_period)
                results[tuple(tickers)] = data
            except Exception as e:
                print(f"Failed to fetch data for {tickers}: {e}")
                continue
        
        return results
    
    def clear_cache(self, older_than_days=None):
        """
        Clear cache files.
        
        Args:
            older_than_days (int, optional): Only clear files older than this many days
        """
        if older_than_days is not None:
            cutoff_time = datetime.now() - timedelta(days=older_than_days)
        
        cleared_count = 0
        for cache_file in self.cache_dir.glob("*.pkl"):
            if older_than_days is None:
                cache_file.unlink()
                cleared_count += 1
            else:
                file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if file_time < cutoff_time:
                    cache_file.unlink()
                    cleared_count += 1
        
        print(f"Cleared {cleared_count} cache files")
    
    def get_cache_info(self):
        """Get information about cached data."""
        cache_files = list(self.cache_dir.glob("*.pkl"))
        
        info = {
            'total_files': len(cache_files),
            'total_size_mb': sum(f.stat().st_size for f in cache_files) / (1024 * 1024),
            'oldest_file': None,
            'newest_file': None
        }
        
        if cache_files:
            file_times = [(f, datetime.fromtimestamp(f.stat().st_mtime)) for f in cache_files]
            file_times.sort(key=lambda x: x[1])
            
            info['oldest_file'] = file_times[0][1]
            info['newest_file'] = file_times[-1][1]
        
        return info
    
    def preload_common_tickers(self, time_periods=[1, 2, 3]):
        """
        Preload cache with common tickers to improve performance.
        
        Args:
            time_periods (list): List of time periods to preload
        """
        common_tickers = [
            ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],  # Tech
            ['VOO', 'VTI', 'VXUS', 'GLD', 'TLT'],       # ETFs
            ['XLK', 'XLF', 'XLV', 'XLE', 'XLI'],        # Sectors
            ['SPY', 'QQQ', 'IWM', 'EFA', 'EEM'],        # Major ETFs
        ]
        
        print("Preloading cache with common tickers...")
        for tickers in common_tickers:
            for period in time_periods:
                try:
                    self.fetch_data(tickers, period)
                    print(f"✓ Cached {tickers} ({period} years)")
                except Exception as e:
                    print(f"✗ Failed to cache {tickers} ({period} years): {e}")
                    continue


# Global data manager instance
_data_manager = None

def get_data_manager():
    """Get or create global data manager instance."""
    global _data_manager
    if _data_manager is None:
        _data_manager = DataManager()
    return _data_manager

def fetch_data_efficient(tickers, time_period=2, force_refresh=False):
    """
    Efficient data fetching function with caching and rate limiting.
    
    Args:
        tickers (list): List of stock tickers
        time_period (int): Number of years of data to fetch
        force_refresh (bool): Force refresh even if cache exists
        
    Returns:
        pandas.DataFrame: Returns data
    """
    data_manager = get_data_manager()
    return data_manager.fetch_data(tickers, time_period, force_refresh)
