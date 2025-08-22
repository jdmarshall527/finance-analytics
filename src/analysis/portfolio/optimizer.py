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
        """Download historical price data and calculate returns."""
        try:
            # Download adjusted close prices
            data = yf.download(self.tickers, start=self.start_date, end=self.end_date)
            
            # Handle single ticker case
            if len(self.tickers) == 1:
                if 'Adj Close' in data.columns:
                    data = pd.DataFrame(data['Adj Close'])
                    data.columns = self.tickers
                else:
                    # Fallback to Close price if Adj Close not available
                    data = pd.DataFrame(data['Close'])
                    data.columns = self.tickers
            else:
                # Multiple tickers - check if Adj Close exists
                if 'Adj Close' in data.columns:
                    data = data['Adj Close']
                else:
                    # Fallback to Close price
                    data = data['Close']
            
            # Calculate daily returns
            self.returns = data.pct_change().dropna()
            
            # Annual expected returns (252 trading days)
            self.mean_returns = self.returns.mean() * 252
            
            # Annual covariance matrix
            self.cov_matrix = self.returns.cov() * 252
            
        except Exception as e:
            raise Exception(f"Error fetching data: {str(e)}")
    
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
        portfolio_return = np.sum(self.mean_returns * weights)
        portfolio_std = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
        sharpe_ratio = portfolio_return / portfolio_std if portfolio_std > 0 else 0
        
        # Calculate inflation-adjusted (real) return
        inflation_rate = self.get_inflation_rate()
        real_return = portfolio_return - inflation_rate
        real_sharpe_ratio = real_return / portfolio_std if portfolio_std > 0 else 0
        
        return {
            'return': portfolio_return,
            'real_return': real_return,
            'volatility': portfolio_std,
            'sharpe_ratio': sharpe_ratio,
            'real_sharpe_ratio': real_sharpe_ratio,
            'inflation_rate': inflation_rate
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
        # Get range of target returns
        min_ret = self.mean_returns.min()
        max_ret = self.mean_returns.max()
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
            except:
                continue
        
        return efficient_portfolios
    
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
        # Generate efficient frontier
        efficient_portfolios = self.generate_efficient_frontier(num_portfolios)
        
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
