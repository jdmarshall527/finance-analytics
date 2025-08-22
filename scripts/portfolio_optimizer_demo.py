#!/usr/bin/env python3
"""
Portfolio Optimizer Demo Script

This script demonstrates how to use the portfolio optimization module
to analyze and optimize investment portfolios.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.analysis.portfolio import analyze_portfolio
import json

def main():
    """Demo the portfolio optimizer with sample data."""
    
    print("=== Portfolio Optimizer Demo ===\n")
    
    # Sample portfolio data
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    weights = [0.3, 0.25, 0.2, 0.15, 0.1]  # Must sum to 1.0
    
    print(f"Analyzing portfolio with {len(tickers)} stocks:")
    for ticker, weight in zip(tickers, weights):
        print(f"  {ticker}: {weight*100:.1f}%")
    print()
    
    try:
        # Analyze the portfolio
        results = analyze_portfolio(tickers, weights)
        
        # Display current portfolio stats
        current = results['current_portfolio']
        print("=== Current Portfolio Performance ===")
        print(f"Expected Annual Return: {current['stats']['return']*100:.2f}%")
        print(f"Annual Volatility: {current['stats']['volatility']*100:.2f}%")
        print(f"Sharpe Ratio: {current['stats']['sharpe_ratio']:.3f}")
        print()
        
        # Display optimal portfolio
        optimal = results['optimal_portfolio']
        print("=== Optimal Portfolio Allocation ===")
        for ticker, weight in optimal['allocation'].items():
            print(f"  {ticker}: {weight*100:.1f}%")
        print()
        print(f"Optimal Expected Return: {optimal['stats']['return']*100:.2f}%")
        print(f"Optimal Volatility: {optimal['stats']['volatility']*100:.2f}%")
        print(f"Optimal Sharpe Ratio: {optimal['stats']['sharpe_ratio']:.3f}")
        print()
        
        # Display recommendations
        print("=== Diversification Recommendations ===")
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"{i}. {rec['ticker']} ({rec['name']})")
            print(f"   Sharpe Improvement: +{rec['sharpe_improvement']:.3f}")
            print(f"   Expected Return: {rec['new_return']*100:.2f}%")
            print(f"   Volatility: {rec['new_volatility']*100:.2f}%")
            print()
        
        # Display analysis summary
        analysis = results['analysis']
        print("=== Analysis Summary ===")
        print(f"Risk Level: {analysis['risk_level']}")
        print(f"Distance from Optimal: +{analysis['distance_from_optimal']:.3f} Sharpe ratio")
        print(f"Efficient Frontier Points: {len(results['efficient_frontier'])}")
        print(f"Random Portfolios Generated: {len(results['random_portfolios'])}")
        
        # Save results to file
        output_file = "data/outputs/portfolio_analysis/portfolio_optimization_results.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to: {output_file}")
        
    except Exception as e:
        print(f"Error analyzing portfolio: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
