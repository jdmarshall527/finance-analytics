# black_litterman.py - Black-Litterman Model Implementation
import numpy as np
import pandas as pd
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

class BlackLittermanModel:
    """
    Black-Litterman Model for portfolio optimization.
    
    The Black-Litterman model combines market equilibrium returns with investor views
    to create more stable and intuitive portfolio allocations.
    """
    
    def __init__(self, tickers, market_caps=None, risk_free_rate=0.02, tau=0.05, delta=2.5):
        """
        Initialize Black-Litterman model.
        
        Args:
            tickers (list): List of stock tickers
            market_caps (list, optional): Market capitalization weights for each asset
            risk_free_rate (float): Risk-free rate (default 2%)
            tau (float): Prior uncertainty parameter (default 0.05)
            delta (float): Risk aversion parameter (default 2.5)
        """
        self.tickers = tickers
        self.n_assets = len(tickers)
        self.risk_free_rate = risk_free_rate
        self.tau = tau
        self.delta = delta
        
        # Market capitalization weights (default to equal weights if not provided)
        if market_caps is None:
            self.market_weights = np.array([1.0 / self.n_assets] * self.n_assets)
        else:
            self.market_weights = np.array(market_caps) / np.sum(market_caps)
        
        # Initialize data structures
        self.returns = None
        self.cov_matrix = None
        self.equilibrium_returns = None
        self.posterior_returns = None
        self.posterior_cov = None
        
    def fetch_data(self, time_period=2):
        """Fetch historical price data using efficient data manager."""
        from .data_manager import fetch_data_efficient
        
        # Use efficient data fetching with caching and rate limiting
        self.returns = fetch_data_efficient(self.tickers, time_period)
        
        # Calculate covariance matrix
        self.cov_matrix = self.returns.cov() * 252  # Annualized
        
        return self.returns
    
    def calculate_equilibrium_returns(self):
        """
        Calculate equilibrium returns using reverse optimization.
        
        Returns:
            array: Equilibrium expected returns
        """
        if self.cov_matrix is None:
            raise ValueError("Must fetch data before calculating equilibrium returns")
        
        # Reverse optimization: Π = δ * Σ * w_market
        self.equilibrium_returns = self.delta * np.dot(self.cov_matrix, self.market_weights)
        
        return self.equilibrium_returns
    
    def add_views(self, views, confidences=None):
        """
        Add investor views to the model.
        
        Args:
            views (list): List of view dictionaries with format:
                         [{'assets': ['AAPL', 'MSFT'], 'view': 0.02, 'type': 'absolute'}]
                         or [{'assets': ['AAPL', 'MSFT'], 'view': 0.01, 'type': 'relative'}]
            confidences (list, optional): Confidence levels for each view (0-1)
        """
        if self.equilibrium_returns is None:
            self.calculate_equilibrium_returns()
        
        n_views = len(views)
        
        # Initialize matrices
        P = np.zeros((n_views, self.n_assets))  # Pick matrix
        Q = np.zeros(n_views)  # View vector
        Omega = np.zeros((n_views, n_views))  # Uncertainty matrix
        
        for i, view in enumerate(views):
            assets = view['assets']
            view_value = view['view']
            view_type = view['type']
            
            # Find asset indices
            asset_indices = [self.tickers.index(asset) for asset in assets]
            
            if view_type == 'absolute':
                # Absolute view: expected return for specific assets
                for j, asset_idx in enumerate(asset_indices):
                    P[i, asset_idx] = 1.0 / len(asset_indices)
                Q[i] = view_value
                
            elif view_type == 'relative':
                # Relative view: difference in expected returns
                if len(asset_indices) >= 2:
                    P[i, asset_indices[0]] = 1.0
                    P[i, asset_indices[1]] = -1.0
                    Q[i] = view_value
                    
                    # For relative views, add weights for remaining assets if any
                    for j in range(2, len(asset_indices)):
                        P[i, asset_indices[j]] = 0.0
            else:
                raise ValueError(f"Unknown view type: {view_type}")
        
        # Set confidence levels (default to 0.5 if not provided)
        if confidences is None:
            confidences = [0.5] * n_views
        
        # Calculate uncertainty matrix
        for i in range(n_views):
            # Use tau * P * Σ * P^T for uncertainty
            omega_i = self.tau * np.dot(P[i], np.dot(self.cov_matrix, P[i]))
            Omega[i, i] = omega_i / confidences[i]
        
        self.P = P
        self.Q = Q
        self.Omega = Omega
        
        return P, Q, Omega
    
    def calculate_posterior_returns(self):
        """
        Calculate posterior returns using Black-Litterman formula.
        
        Returns:
            array: Posterior expected returns
        """
        if not hasattr(self, 'P') or not hasattr(self, 'Q') or not hasattr(self, 'Omega'):
            raise ValueError("Must add views before calculating posterior returns")
        
        # Prior precision matrix
        tau_sigma = self.tau * self.cov_matrix
        tau_sigma_inv = np.linalg.inv(tau_sigma)
        
        # View precision matrix
        omega_inv = np.linalg.inv(self.Omega)
        
        # Posterior precision matrix
        posterior_precision = tau_sigma_inv + np.dot(self.P.T, np.dot(omega_inv, self.P))
        
        # Posterior returns
        posterior_mean = np.dot(
            np.linalg.inv(posterior_precision),
            np.dot(tau_sigma_inv, self.equilibrium_returns) + 
            np.dot(self.P.T, np.dot(omega_inv, self.Q))
        )
        
        # Posterior covariance
        self.posterior_cov = np.linalg.inv(posterior_precision)
        self.posterior_returns = posterior_mean
        
        return self.posterior_returns
    
    def optimize_portfolio(self, constraint='max_sharpe', min_weight=0.0, max_weight=1.0):
        """
        Optimize portfolio using posterior returns.
        
        Args:
            constraint (str): Optimization constraint ('max_sharpe' or 'min_volatility')
            min_weight (float): Minimum weight per asset
            max_weight (float): Maximum weight per asset
            
        Returns:
            array: Optimal portfolio weights
        """
        # If no views were added, use equilibrium returns
        if self.posterior_returns is None:
            if self.equilibrium_returns is None:
                self.calculate_equilibrium_returns()
            returns = self.equilibrium_returns
            cov_matrix = self.cov_matrix
        else:
            returns = self.posterior_returns
            cov_matrix = self.posterior_cov if self.posterior_cov is not None else self.cov_matrix
        
        if constraint == 'max_sharpe':
            # Maximize Sharpe ratio
            def objective(weights):
                portfolio_return = np.sum(returns * weights)
                portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                sharpe = (portfolio_return - self.risk_free_rate) / portfolio_vol
                return -sharpe  # Minimize negative Sharpe ratio
            
        elif constraint == 'min_volatility':
            # Minimize volatility
            def objective(weights):
                portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                return portfolio_vol
        else:
            raise ValueError(f"Unknown constraint: {constraint}")
        
        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0}  # Weights sum to 1
        ]
        
        # Bounds
        bounds = [(min_weight, max_weight)] * self.n_assets
        
        # Initial guess (equal weights)
        initial_weights = np.array([1.0 / self.n_assets] * self.n_assets)
        
        # Optimize
        result = minimize(
            objective,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'ftol': 1e-8, 'maxiter': 1000}
        )
        
        if not result.success:
            warnings.warn(f"Optimization failed: {result.message}")
        
        return result.x
    
    def portfolio_stats(self, weights):
        """
        Calculate portfolio statistics using posterior returns.
        
        Args:
            weights (array): Portfolio weights
            
        Returns:
            dict: Portfolio statistics
        """
        # If no views were added, use equilibrium returns
        if self.posterior_returns is None:
            if self.equilibrium_returns is None:
                self.calculate_equilibrium_returns()
            returns = self.equilibrium_returns
            cov_matrix = self.cov_matrix
        else:
            returns = self.posterior_returns
            cov_matrix = self.posterior_cov if self.posterior_cov is not None else self.cov_matrix
        
        portfolio_return = np.sum(returns * weights)
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol if portfolio_vol > 0 else 0
        
        # Calculate inflation-adjusted returns
        inflation_rate = 0.025  # 2.5% default inflation rate
        real_return = portfolio_return - inflation_rate
        real_sharpe_ratio = real_return / portfolio_vol if portfolio_vol > 0 else 0
        
        return {
            'return': float(portfolio_return),
            'real_return': float(real_return),
            'volatility': float(portfolio_vol),
            'sharpe_ratio': float(sharpe_ratio),
            'real_sharpe_ratio': float(real_sharpe_ratio),
            'inflation_rate': float(inflation_rate)
        }
    
    def generate_efficient_frontier(self, num_portfolios=50):
        """
        Generate efficient frontier using posterior returns.
        
        Args:
            num_portfolios (int): Number of portfolios to generate
            
        Returns:
            list: List of portfolio dictionaries
        """
        # If no views were added, use equilibrium returns
        if self.posterior_returns is None:
            if self.equilibrium_returns is None:
                self.calculate_equilibrium_returns()
            returns = self.equilibrium_returns
            cov_matrix = self.cov_matrix
        else:
            returns = self.posterior_returns
            cov_matrix = self.posterior_cov if self.posterior_cov is not None else self.cov_matrix
        
        # Generate target returns
        min_return = np.min(returns)
        max_return = np.max(returns)
        target_returns = np.linspace(min_return, max_return, num_portfolios)
        
        efficient_portfolios = []
        
        for target_return in target_returns:
            try:
                # Minimize volatility for given target return
                def objective(weights):
                    portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                    return portfolio_vol
                
                constraints = [
                    {'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0},
                    {'type': 'eq', 'fun': lambda x: np.sum(returns * x) - target_return}
                ]
                
                bounds = [(0.0, 1.0)] * self.n_assets
                initial_weights = np.array([1.0 / self.n_assets] * self.n_assets)
                
                result = minimize(
                    objective,
                    initial_weights,
                    method='SLSQP',
                    bounds=bounds,
                    constraints=constraints,
                    options={'ftol': 1e-8, 'maxiter': 1000}
                )
                
                if result.success:
                    weights = result.x
                    portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                    sharpe_ratio = (target_return - self.risk_free_rate) / portfolio_vol if portfolio_vol > 0 else 0
                    
                    efficient_portfolios.append({
                        'return': float(target_return),
                        'volatility': float(portfolio_vol),
                        'sharpe_ratio': float(sharpe_ratio),
                        'weights': weights.tolist()
                    })
                    
            except Exception as e:
                continue
        
        return efficient_portfolios


def analyze_portfolio_black_litterman(tickers, weights, views=None, time_period=2, 
                                    market_caps=None, risk_free_rate=0.02):
    """
    Analyze portfolio using Black-Litterman model.
    
    Args:
        tickers (list): List of stock tickers
        weights (list): Current portfolio weights
        views (list, optional): Investor views
        time_period (int): Years of historical data
        market_caps (list, optional): Market capitalization weights
        risk_free_rate (float): Risk-free rate
        
    Returns:
        dict: Analysis results
    """
    # Initialize Black-Litterman model
    bl_model = BlackLittermanModel(tickers, market_caps, risk_free_rate)
    
    # Fetch data
    bl_model.fetch_data(time_period)
    
    # Calculate equilibrium returns
    equilibrium_returns = bl_model.calculate_equilibrium_returns()
    
    # Add views if provided
    if views:
        bl_model.add_views(views)
        bl_model.calculate_posterior_returns()
        returns_for_analysis = bl_model.posterior_returns
        cov_for_analysis = bl_model.posterior_cov
    else:
        returns_for_analysis = equilibrium_returns
        cov_for_analysis = bl_model.cov_matrix
    
    # Calculate current portfolio stats
    current_stats = {
        'return': float(np.sum(returns_for_analysis * weights)),
        'volatility': float(np.sqrt(np.dot(weights, np.dot(cov_for_analysis, weights)))),
        'sharpe_ratio': float((np.sum(returns_for_analysis * weights) - risk_free_rate) / 
                             np.sqrt(np.dot(weights, np.dot(cov_for_analysis, weights))))
    }
    
    # Optimize portfolio
    optimal_weights = bl_model.optimize_portfolio('max_sharpe')
    optimal_stats = bl_model.portfolio_stats(optimal_weights)
    
    # Generate efficient frontier
    efficient_frontier = bl_model.generate_efficient_frontier(50)
    
    return {
        'current_portfolio': {
            'tickers': tickers,
            'weights': weights,
            'stats': current_stats
        },
        'optimal_portfolio': {
            'weights': optimal_weights.tolist(),
            'stats': optimal_stats,
            'allocation': {tickers[i]: optimal_weights[i] for i in range(len(tickers))}
        },
        'equilibrium_returns': equilibrium_returns.tolist(),
        'posterior_returns': returns_for_analysis.tolist() if views else None,
        'efficient_frontier': efficient_frontier,
        'views_used': views is not None,
        'analysis': {
            'time_period': f"{time_period} years",
            'risk_free_rate': f"{risk_free_rate*100:.1f}%",
            'model_type': 'Black-Litterman'
        }
    }
