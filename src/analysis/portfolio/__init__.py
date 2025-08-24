# Portfolio Analysis Module
"""
Portfolio analysis and optimization tools using Modern Portfolio Theory.

This module provides tools for:
- Portfolio optimization using Modern Portfolio Theory
- Efficient frontier calculation
- Risk-adjusted return analysis
- Diversification recommendations
- Portfolio performance metrics
- Black-Litterman model for incorporating investor views
"""

from .optimizer import PortfolioOptimizer, analyze_portfolio, analyze_portfolio_with_period, get_sector_etfs
from .black_litterman import BlackLittermanModel, analyze_portfolio_black_litterman
from .data_manager import DataManager, get_data_manager, fetch_data_efficient

__all__ = [
    'PortfolioOptimizer',
    'analyze_portfolio',
    'analyze_portfolio_with_period',
    'get_sector_etfs',
    'BlackLittermanModel',
    'analyze_portfolio_black_litterman',
    'DataManager',
    'get_data_manager',
    'fetch_data_efficient'
]
