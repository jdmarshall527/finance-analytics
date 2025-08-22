# Portfolio Analysis Module
"""
Portfolio analysis and optimization tools using Modern Portfolio Theory.

This module provides tools for:
- Portfolio optimization using Modern Portfolio Theory
- Efficient frontier calculation
- Risk-adjusted return analysis
- Diversification recommendations
- Portfolio performance metrics
"""

from .optimizer import PortfolioOptimizer, analyze_portfolio, analyze_portfolio_with_period, get_sector_etfs

__all__ = [
    'PortfolioOptimizer',
    'analyze_portfolio',
    'analyze_portfolio_with_period',
    'get_sector_etfs'
]
