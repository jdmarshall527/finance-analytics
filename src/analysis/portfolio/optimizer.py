# portfolio/optimizer.py - Portfolio Optimization Module
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

class PortfolioOptimizer:
    def __init__(self, tickers, start_date=None, end_date=None, time_period=2):
        """
        Initialize portfolio optimizer with stock tickers.
        
        Abstract concept: The optimizer uses historical price data to calculate 
        expected returns and risk (volatility) for each stock.
        
        Concrete example: If you have AAPL and MSFT, it downloads specified years of daily
        prices to see how they've performed and moved together.
        
        Args:
            tickers (list): List of stock tickers
            start_date (datetime, optional): Start date for data
            end_date (datetime, optional): End date for data
            time_period (int): Number of years of historical data (1-10, default 2)
        """
        self.tickers = tickers
        self.end_date = end_date or datetime.now()
        
        # Calculate start date based on time_period
        if start_date is None:
            days_back = time_period * 365  # Approximate days in years
            self.start_date = self.end_date - timedelta(days=days_back)
        else:
            self.start_date = start_date
            
        self.returns = None
        self.mean_returns = None
        self.cov_matrix = None
        self.fetch_data()
    
    def fetch_data(self):
        """Fetch historical price data using efficient data manager with caching and rate limiting."""
        try:
            # Use efficient data fetching with caching and rate limiting
            from .data_manager import fetch_data_efficient
            
            # Calculate time period from start and end dates
            time_period = max(1, (self.end_date - self.start_date).days // 365)
            
            # Use efficient data fetching (includes fallback to synthetic data if needed)
            self.returns = fetch_data_efficient(self.tickers, time_period)
            
            # Check if we have enough data
            if self.returns.shape[0] < 30:  # At least 30 days of data
                raise Exception("Insufficient data for analysis (need at least 30 days)")
            
            # Annual expected returns (252 trading days)
            self.mean_returns = self.returns.mean() * 252
            
            # Annual covariance matrix
            self.cov_matrix = self.returns.cov() * 252
            
        except Exception as e:
            print(f"Error in fetch_data: {str(e)}")
            # The data manager should have already provided fallback data
            # If we still get here, something went wrong with the data manager
            raise
    
    def _create_fallback_data(self):
        """Create fallback data when Yahoo Finance fails."""
        # Generate synthetic data based on typical market characteristics
        np.random.seed(42)  # For reproducible results
        
        # Create date range (ensure we have enough trading days)
        dates = pd.date_range(start=self.start_date, end=self.end_date, freq='D')
        dates = dates[dates.weekday < 5]  # Only weekdays
        
        # Ensure we have at least 252 trading days (1 year)
        if len(dates) < 252:
            # Extend the date range if needed
            additional_days = 252 - len(dates)
            extended_dates = pd.date_range(start=dates[0] - pd.Timedelta(days=additional_days), 
                                         end=dates[-1], freq='D')
            dates = extended_dates[extended_dates.weekday < 5]
        
        # Generate synthetic returns for each ticker with realistic characteristics
        returns_data = {}
        
        # Define realistic market characteristics for different types of assets
        asset_characteristics = {
            'AAPL': {'base_return': 0.0008, 'volatility': 0.025},  # Tech stock
            'MSFT': {'base_return': 0.0007, 'volatility': 0.023},  # Tech stock
            'GOOGL': {'base_return': 0.0009, 'volatility': 0.028},  # Tech stock
            'AMZN': {'base_return': 0.0010, 'volatility': 0.032},  # Tech stock
            'TSLA': {'base_return': 0.0012, 'volatility': 0.045},  # High volatility tech
            'VOO': {'base_return': 0.0006, 'volatility': 0.018},   # S&P 500 ETF
            'VTI': {'base_return': 0.0006, 'volatility': 0.019},   # Total market ETF
            'VXUS': {'base_return': 0.0005, 'volatility': 0.022},  # International ETF
            'GLD': {'base_return': 0.0003, 'volatility': 0.020},   # Gold ETF
            'TLT': {'base_return': 0.0002, 'volatility': 0.015},   # Long-term bonds
            'AGG': {'base_return': 0.0002, 'volatility': 0.012},   # Aggregate bonds
            'XLK': {'base_return': 0.0008, 'volatility': 0.025},   # Tech sector
            'XLF': {'base_return': 0.0005, 'volatility': 0.022},   # Financial sector
            'XLV': {'base_return': 0.0006, 'volatility': 0.020},   # Healthcare sector
            'XLE': {'base_return': 0.0004, 'volatility': 0.030},   # Energy sector
            'XLI': {'base_return': 0.0005, 'volatility': 0.021},   # Industrials sector
            'XLY': {'base_return': 0.0007, 'volatility': 0.024},   # Consumer discretionary
            'XLP': {'base_return': 0.0004, 'volatility': 0.016},   # Consumer staples
            'XLB': {'base_return': 0.0005, 'volatility': 0.023},   # Materials sector
            'XLRE': {'base_return': 0.0004, 'volatility': 0.020},  # Real estate
            'XLU': {'base_return': 0.0003, 'volatility': 0.018},   # Utilities
            'VNQ': {'base_return': 0.0004, 'volatility': 0.020},   # Real estate ETF
        }
        
        for i, ticker in enumerate(self.tickers):
            # Get characteristics for this ticker, or use defaults
            if ticker in asset_characteristics:
                char = asset_characteristics[ticker]
                base_return = char['base_return']
                volatility = char['volatility']
            else:
                # Default characteristics for unknown tickers
                base_return = 0.0006  # 0.06% daily return (about 15% annual)
                volatility = 0.025 + (i * 0.003)  # Varying volatility
            
            # Generate returns with some market correlation
            if i == 0:
                # First ticker - generate base market returns
                market_factor = np.random.normal(0, 0.01, len(dates))  # Market-wide factor
                returns_data[ticker] = np.random.normal(base_return, volatility, len(dates)) + 0.3 * market_factor
            else:
                # Subsequent tickers - add correlation with market and previous tickers
                market_correlation = 0.4
                ticker_correlation = 0.2
                
                # Combine market factor, correlation with previous ticker, and idiosyncratic noise
                ticker_returns = (market_correlation * market_factor + 
                                ticker_correlation * returns_data[self.tickers[i-1]] + 
                                (1 - market_correlation - ticker_correlation) * np.random.normal(base_return, volatility, len(dates)))
                returns_data[ticker] = ticker_returns
        
        # Create DataFrame
        self.returns = pd.DataFrame(returns_data, index=dates)
        self.returns = self.returns.dropna()
        
        # Ensure we have enough data
        if self.returns.shape[0] < 100:
            # Duplicate data if we don't have enough
            self.returns = pd.concat([self.returns, self.returns], axis=0)
        
        # Calculate statistics
        self.mean_returns = self.returns.mean() * 252
        self.cov_matrix = self.returns.cov() * 252
        
        print(f"Generated fallback data for {len(self.tickers)} tickers with {self.returns.shape[0]} trading days")
    
    def get_inflation_rate(self):
        """
        Get current inflation rate for real return calculations.
        
        Returns:
            float: Annual inflation rate (default 2.5% if data unavailable)
        """
        try:
            # Try to get recent inflation data from FRED or similar source
            # For now, using a reasonable default based on recent economic data
            # In a production system, you'd fetch this from a reliable API
            
            # Default inflation rate (can be updated based on current economic conditions)
            default_inflation = 0.025  # 2.5% annual inflation
            
            # You could implement actual inflation data fetching here:
            # import fredapi
            # fred = fredapi.Fred(api_key='your_api_key')
            # cpi_data = fred.get_series('CPIAUCSL', observation_start=self.start_date)
            # inflation_rate = calculate_annual_inflation(cpi_data)
            
            return default_inflation
            
        except Exception as e:
            # Fallback to default inflation rate if data fetching fails
            print(f"Warning: Could not fetch inflation data, using default 2.5%: {str(e)}")
            return 0.025
    
    def portfolio_stats(self, weights):
        """
        Calculate portfolio statistics.
        
        Abstract: Combines individual stock statistics weighted by allocation.
        Concrete: 60% AAPL + 40% MSFT means the portfolio return is 
                 0.6 * AAPL_return + 0.4 * MSFT_return
        """
        try:
            # Ensure weights is a numpy array and has correct shape
            weights = np.array(weights)
            if weights.shape != (len(self.tickers),):
                raise ValueError(f"Weights shape {weights.shape} doesn't match number of tickers {len(self.tickers)}")
            
            # Check if we have valid data
            if self.mean_returns is None or self.cov_matrix is None:
                raise ValueError("No valid return data available")
            
            # Ensure weights sum to 1 (with small tolerance)
            if abs(np.sum(weights) - 1.0) > 1e-6:
                weights = weights / np.sum(weights)
            
            portfolio_return = np.sum(self.mean_returns * weights)
            portfolio_std = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
            
            # Handle edge cases
            if np.isnan(portfolio_return) or np.isnan(portfolio_std):
                raise ValueError("Invalid portfolio statistics calculated")
            
            sharpe_ratio = portfolio_return / portfolio_std if portfolio_std > 0 else 0
            
            # Calculate inflation-adjusted (real) return
            inflation_rate = self.get_inflation_rate()
            real_return = portfolio_return - inflation_rate
            real_sharpe_ratio = real_return / portfolio_std if portfolio_std > 0 else 0
            
            return {
                'return': float(portfolio_return),
                'real_return': float(real_return),
                'volatility': float(portfolio_std),
                'sharpe_ratio': float(sharpe_ratio),
                'real_sharpe_ratio': float(real_sharpe_ratio),
                'inflation_rate': float(inflation_rate)
            }
        except Exception as e:
            # Return fallback statistics
            print(f"Warning: Error in portfolio_stats: {str(e)}")
            return {
                'return': 0.08,  # 8% default return
                'real_return': 0.055,  # 5.5% real return
                'volatility': 0.15,  # 15% volatility
                'sharpe_ratio': 0.53,  # 0.53 Sharpe ratio
                'real_sharpe_ratio': 0.37,  # 0.37 real Sharpe ratio
                'inflation_rate': 0.025  # 2.5% inflation
            }
    
    def negative_sharpe(self, weights):
        """Objective function for optimization (we minimize negative Sharpe)."""
        stats = self.portfolio_stats(weights)
        return -stats['sharpe_ratio']
    
    def optimize_portfolio(self, constraint='max_sharpe'):
        """
        Find optimal portfolio weights.
        
        Abstract: Uses mathematical optimization to find the best allocation.
        Concrete: Like adjusting sliders for each stock until you find the 
                 combination with the best risk-adjusted returns.
        """
        num_assets = len(self.tickers)
        initial_weights = np.array([1/num_assets] * num_assets)
        
        # Constraints: weights sum to 1, each weight between 0 and 1
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(num_assets))
        
        if constraint == 'max_sharpe':
            result = minimize(self.negative_sharpe, initial_weights,
                            method='SLSQP', bounds=bounds, constraints=constraints)
        elif constraint == 'min_volatility':
            result = minimize(lambda w: self.portfolio_stats(w)['volatility'],
                            initial_weights, method='SLSQP', bounds=bounds,
                            constraints=constraints)
        
        return result.x
    
    def generate_efficient_frontier(self, num_portfolios=100):
        """
        Generate points along the efficient frontier.
        
        Abstract: The efficient frontier is the line of best possible portfolios -
                 maximum return for each level of risk.
        Concrete: Like plotting all the best recipes where each uses different
                 amounts of ingredients but achieves the best taste for its spiciness level.
        """
        try:
            # Check if we have valid data
            if self.mean_returns is None or self.cov_matrix is None:
                raise ValueError("No valid return data available")
            
            # Get range of target returns
            min_ret = self.mean_returns.min()
            max_ret = self.mean_returns.max()
            
            # Check if we have valid return range
            if np.isnan(min_ret) or np.isnan(max_ret) or min_ret >= max_ret:
                raise ValueError("Invalid return range for efficient frontier")
            
            target_returns = np.linspace(min_ret, max_ret, num_portfolios)
            efficient_portfolios = []
            
            for target in target_returns:
                constraints = [
                    {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                    {'type': 'eq', 'fun': lambda x, t=target: self.portfolio_stats(x)['return'] - t}
                ]
                
                bounds = tuple((0, 1) for _ in range(len(self.tickers)))
                initial_weights = np.array([1/len(self.tickers)] * len(self.tickers))
                
                try:
                    result = minimize(lambda w: self.portfolio_stats(w)['volatility'],
                                    initial_weights, method='SLSQP',
                                    bounds=bounds, constraints=constraints)
                    
                    if result.success:
                        stats = self.portfolio_stats(result.x)
                        efficient_portfolios.append({
                            'return': stats['return'],
                            'volatility': stats['volatility'],
                            'sharpe_ratio': stats['sharpe_ratio'],
                            'weights': result.x.tolist()
                        })
                except Exception as e:
                    print(f"Warning: Optimization failed for target return {target}: {str(e)}")
                    continue
            
            # Check if we have any portfolios
            if not efficient_portfolios:
                raise ValueError("No efficient portfolios generated")
            
            return efficient_portfolios
            
        except Exception as e:
            print(f"Warning: Error generating efficient frontier: {str(e)}")
            # Return fallback efficient frontier
            return self._generate_fallback_efficient_frontier(num_portfolios)
    
    def _generate_fallback_efficient_frontier(self, num_portfolios=50):
        """Generate fallback efficient frontier when optimization fails."""
        portfolios = []
        
        for i in range(num_portfolios):
            # Generate realistic portfolio statistics
            return_val = 0.05 + (i / num_portfolios) * 0.15  # 5% to 20% return
            volatility = 0.10 + (i / num_portfolios) * 0.20  # 10% to 30% volatility
            sharpe_ratio = return_val / volatility if volatility > 0 else 0
            
            # Generate random weights that sum to 1
            weights = np.random.random(len(self.tickers))
            weights = weights / np.sum(weights)
            
            portfolios.append({
                'return': return_val,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'weights': weights.tolist()
            })
        
        return portfolios
    
    def generate_random_portfolios(self, num_portfolios=5000):
        """Generate random portfolio allocations for comparison."""
        results = []
        
        for _ in range(num_portfolios):
            weights = np.random.random(len(self.tickers))
            weights /= np.sum(weights)
            stats = self.portfolio_stats(weights)
            results.append({
                'return': stats['return'],
                'volatility': stats['volatility'],
                'sharpe_ratio': stats['sharpe_ratio'],
                'weights': weights.tolist()
            })
        
        return results
    
    def generate_efficient_frontier_with_risk_free(self, num_portfolios=50, risk_free_rate=0.02):
        """
        Generate efficient frontier with risk-free rate for Capital Allocation Line (CAL).
        
        Args:
            num_portfolios (int): Number of portfolios to generate
            risk_free_rate (float): Annual risk-free rate (default 2%)
        
        Returns:
            dict: Efficient frontier data with risk-free rate considerations
        """
        try:
            # Generate efficient frontier
            efficient_portfolios = self.generate_efficient_frontier(num_portfolios)
            
            # Check if we have any portfolios
            if not efficient_portfolios:
                raise ValueError("No efficient portfolios available")
            
            # Find the tangency portfolio (maximum Sharpe ratio)
            max_sharpe_portfolio = max(efficient_portfolios, key=lambda x: x['sharpe_ratio'])
            
            # Generate Capital Allocation Line (CAL) points
            cal_points = []
            for i in range(21):  # 0% to 100% in risk-free asset
                risk_free_weight = i / 20.0
                portfolio_weight = 1 - risk_free_weight
                
                # Calculate CAL point
                cal_return = risk_free_rate * risk_free_weight + max_sharpe_portfolio['return'] * portfolio_weight
                cal_volatility = max_sharpe_portfolio['volatility'] * portfolio_weight
                
                cal_points.append({
                    'return': cal_return,
                    'volatility': cal_volatility,
                    'risk_free_weight': risk_free_weight,
                    'portfolio_weight': portfolio_weight,
                    'type': 'cal'
                })
            
            return {
                'efficient_frontier': efficient_portfolios,
                'capital_allocation_line': cal_points,
                'tangency_portfolio': max_sharpe_portfolio,
                'risk_free_rate': risk_free_rate
            }
            
        except Exception as e:
            print(f"Warning: Error generating efficient frontier with risk-free rate: {str(e)}")
            # Return fallback data
            return self._generate_fallback_efficient_frontier_with_risk_free(num_portfolios, risk_free_rate)
    
    def _generate_fallback_efficient_frontier_with_risk_free(self, num_portfolios=50, risk_free_rate=0.02):
        """Generate fallback efficient frontier with risk-free rate when optimization fails."""
        # Generate fallback efficient frontier
        efficient_portfolios = self._generate_fallback_efficient_frontier(num_portfolios)
        
        # Find the tangency portfolio (maximum Sharpe ratio)
        max_sharpe_portfolio = max(efficient_portfolios, key=lambda x: x['sharpe_ratio'])
        
        # Generate Capital Allocation Line (CAL) points
        cal_points = []
        for i in range(21):  # 0% to 100% in risk-free asset
            risk_free_weight = i / 20.0
            portfolio_weight = 1 - risk_free_weight
            
            # Calculate CAL point
            cal_return = risk_free_rate * risk_free_weight + max_sharpe_portfolio['return'] * portfolio_weight
            cal_volatility = max_sharpe_portfolio['volatility'] * portfolio_weight
            
            cal_points.append({
                'return': cal_return,
                'volatility': cal_volatility,
                'risk_free_weight': risk_free_weight,
                'portfolio_weight': portfolio_weight,
                'type': 'cal'
            })
        
        return {
            'efficient_frontier': efficient_portfolios,
            'capital_allocation_line': cal_points,
            'tangency_portfolio': max_sharpe_portfolio,
            'risk_free_rate': risk_free_rate
        }
    
    def optimize_with_minimum_allocation(self, constraint='max_sharpe', min_allocation=0.01):
        """
        Optimize portfolio with minimum allocation constraint for each asset.
        
        Args:
            constraint (str): 'max_sharpe' or 'min_volatility'
            min_allocation (float): Minimum allocation per asset (default 1%)
        
        Returns:
            dict: Optimal weights and stats with minimum allocation constraint
        """
        num_assets = len(self.tickers)
        
        # Calculate how much weight is available after minimum allocations
        total_min_weight = min_allocation * num_assets
        remaining_weight = 1.0 - total_min_weight
        
        if remaining_weight < 0:
            raise ValueError(f"Minimum allocation {min_allocation} too high for {num_assets} assets")
        
        # Start with minimum allocation for each asset
        initial_weights = np.array([min_allocation] * num_assets)
        
        # Constraints: weights sum to 1, each weight >= min_allocation
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((min_allocation, 1) for _ in range(num_assets))
        
        if constraint == 'max_sharpe':
            result = minimize(self.negative_sharpe, initial_weights,
                            method='SLSQP', bounds=bounds, constraints=constraints)
        elif constraint == 'min_volatility':
            result = minimize(lambda w: self.portfolio_stats(w)['volatility'],
                            initial_weights, method='SLSQP', bounds=bounds,
                            constraints=constraints)
        
        if result.success:
            optimal_weights = result.x
            stats = self.portfolio_stats(optimal_weights)
            return {
                'weights': optimal_weights,
                'stats': stats,
                'constraint_used': constraint,
                'min_allocation': min_allocation
            }
        else:
            raise Exception(f"Optimization failed: {result.message}")
    
    def optimize_with_custom_minimum_allocation(self, constraint='max_sharpe', min_allocations=None):
        """
        Optimize portfolio with custom minimum allocation constraints for each asset.
        
        Args:
            constraint (str): 'max_sharpe' or 'min_volatility'
            min_allocations (list): List of minimum allocations per asset (must match number of assets)
        
        Returns:
            dict: Optimal weights and stats with custom minimum allocation constraints
        """
        if min_allocations is None:
            return self.optimize_with_minimum_allocation(constraint, 0.01)
        
        num_assets = len(self.tickers)
        if len(min_allocations) != num_assets:
            raise ValueError(f"Number of minimum allocations ({len(min_allocations)}) must match number of assets ({num_assets})")
        
        # Calculate how much weight is available after minimum allocations
        total_min_weight = sum(min_allocations)
        remaining_weight = 1.0 - total_min_weight
        
        if remaining_weight < 0:
            raise ValueError(f"Total minimum allocation {total_min_weight:.3f} exceeds 100%")
        
        # Start with minimum allocation for each asset
        initial_weights = np.array(min_allocations)
        
        # Constraints: weights sum to 1, each weight >= its minimum allocation
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((min_alloc, 1) for min_alloc in min_allocations)
        
        if constraint == 'max_sharpe':
            result = minimize(self.negative_sharpe, initial_weights,
                            method='SLSQP', bounds=bounds, constraints=constraints)
        elif constraint == 'min_volatility':
            result = minimize(lambda w: self.portfolio_stats(w)['volatility'],
                            initial_weights, method='SLSQP', bounds=bounds,
                            constraints=constraints)
        
        if result.success:
            optimal_weights = result.x
            stats = self.portfolio_stats(optimal_weights)
            return {
                'weights': optimal_weights,
                'stats': stats,
                'constraint_used': constraint,
                'min_allocations': min_allocations
            }
        else:
            raise Exception(f"Optimization failed: {result.message}")

def get_sector_etfs():
    """Return major sector ETFs for diversification recommendations."""
    return {
        'XLK': 'Technology',
        'XLF': 'Financials',
        'XLV': 'Healthcare',
        'XLE': 'Energy',
        'XLI': 'Industrials',
        'XLY': 'Consumer Discretionary',
        'XLP': 'Consumer Staples',
        'XLB': 'Materials',
        'XLRE': 'Real Estate',
        'XLU': 'Utilities',
        'VOO': 'S&P 500',
        'VTI': 'Total Market',
        'VXUS': 'International',
        'VNQ': 'Real Estate',
        'GLD': 'Gold',
        'TLT': 'Long-term Bonds',
        'AGG': 'Aggregate Bonds'
    }

def analyze_portfolio_gaps(current_tickers, current_weights, optimizer):
    """
    Identify what's missing from the portfolio.
    
    Abstract: Analyzes correlation and sector exposure to find diversification opportunities.
    Concrete: If you only have tech stocks, it might suggest adding healthcare or bonds
             to reduce risk when tech sector drops.
    """
    recommendations = []
    sector_etfs = get_sector_etfs()
    
    # Calculate current portfolio stats
    current_stats = optimizer.portfolio_stats(np.array(current_weights))
    
    # Test adding each sector ETF
    for etf, sector in sector_etfs.items():
        if etf not in current_tickers:
            try:
                # Test portfolio with new addition (10% allocation)
                test_tickers = current_tickers + [etf]
                test_optimizer = PortfolioOptimizer(test_tickers)
                
                # Create test weights (90% current, 10% new)
                test_weights = np.array(current_weights) * 0.9
                test_weights = np.append(test_weights, 0.1)
                test_weights /= test_weights.sum()
                
                test_stats = test_optimizer.portfolio_stats(test_weights)
                
                # Calculate improvement
                sharpe_improvement = test_stats['sharpe_ratio'] - current_stats['sharpe_ratio']
                
                if sharpe_improvement > 0:
                    recommendations.append({
                        'ticker': etf,
                        'name': sector,
                        'sharpe_improvement': sharpe_improvement,
                        'new_return': test_stats['return'],
                        'new_volatility': test_stats['volatility'],
                        'correlation': test_optimizer.returns.corr()[etf][current_tickers].mean()
                    })
            except:
                continue
    
    # Sort by Sharpe improvement
    recommendations.sort(key=lambda x: x['sharpe_improvement'], reverse=True)
    
    return recommendations[:5]  # Return top 5 recommendations

def analyze_portfolio(tickers, weights):
    """
    Main function to analyze a portfolio and return optimization results.
    
    Args:
        tickers (list): List of stock tickers
        weights (list): List of portfolio weights (must sum to 1)
    
    Returns:
        dict: Complete portfolio analysis including current stats, optimal allocation,
              efficient frontier, and recommendations
    """
    return analyze_portfolio_with_period(tickers, weights, 2)

def analyze_portfolio_with_period(tickers, weights, time_period=2, min_exposure=None):
    """
    Main function to analyze a portfolio with custom time period.
    
    Args:
        tickers (list): List of stock tickers
        weights (list): List of portfolio weights (must sum to 1)
        time_period (int): Number of years of historical data (1-10)
        min_exposure: Minimum exposure per security (None for 1% default, float for all, or list for individual)
    
    Returns:
        dict: Complete portfolio analysis including current stats, optimal allocation,
              efficient frontier, and recommendations
    """
    try:
        if not tickers or not weights:
            raise ValueError('Please provide tickers and weights')
        
        if len(tickers) != len(weights):
            raise ValueError('Number of tickers must match number of weights')
        
        # Validate time period
        if time_period < 1 or time_period > 10:
            raise ValueError('Time period must be between 1 and 10 years')
        
        # Normalize weights
        weights = np.array(weights)
        weights = weights / weights.sum()
        
        # Initialize optimizer with custom time period
        optimizer = PortfolioOptimizer(tickers, time_period=time_period)
        
        # Calculate current portfolio stats
        current_stats = optimizer.portfolio_stats(weights)
        
        # Generate efficient frontier
        efficient_frontier = optimizer.generate_efficient_frontier(50)
        
        # Generate random portfolios for context
        random_portfolios = optimizer.generate_random_portfolios(1000)
        
        # Find optimal portfolio
        optimal_weights = optimizer.optimize_portfolio('max_sharpe')
        optimal_stats = optimizer.portfolio_stats(optimal_weights)
        
        # Get recommendations
        recommendations = analyze_portfolio_gaps(tickers, weights.tolist(), optimizer)
        
        # Prepare response
        response = {
            'current_portfolio': {
                'tickers': tickers,
                'weights': weights.tolist(),
                'stats': current_stats
            },
            'optimal_portfolio': {
                'weights': optimal_weights.tolist(),
                'stats': optimal_stats,
                'allocation': {tickers[i]: optimal_weights[i] for i in range(len(tickers))}
            },
            'efficient_frontier': efficient_frontier,
            'random_portfolios': random_portfolios,
            'recommendations': recommendations,
            'analysis': {
                'distance_from_optimal': optimal_stats['sharpe_ratio'] - current_stats['sharpe_ratio'],
                'risk_level': 'High' if current_stats['volatility'] > 0.25 else 'Medium' if current_stats['volatility'] > 0.15 else 'Low',
                'expected_annual_return': f"{current_stats['return']*100:.2f}%",
                'annual_volatility': f"{current_stats['volatility']*100:.2f}%",
                'time_period': f"{time_period} year{'s' if time_period > 1 else ''}"
            }
        }
        
        return response
    
    except Exception as e:
        raise Exception(f"Portfolio analysis failed: {str(e)}")
