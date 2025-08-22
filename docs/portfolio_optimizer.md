# Portfolio Optimizer Documentation

## Overview

The Portfolio Optimizer module provides comprehensive tools for portfolio analysis and optimization using Modern Portfolio Theory (MPT). It helps investors construct optimal portfolios that maximize expected returns for a given level of risk.

## Features

- **Portfolio Analysis**: Analyze current portfolio performance and risk metrics
- **Efficient Frontier**: Generate the optimal risk-return frontier
- **Portfolio Optimization**: Find optimal asset allocations using mathematical optimization
- **Diversification Recommendations**: Get suggestions for improving portfolio diversification
- **Risk Metrics**: Calculate Sharpe ratio, volatility, and expected returns
- **Web API**: RESTful API for integration with web applications

## Core Concepts

### Modern Portfolio Theory (MPT)

MPT states that investors can construct portfolios to maximize expected return based on a given level of market risk. The key insight is that securities can be combined in a portfolio where the portfolio's total risk is less than the sum of individual risks due to diversification.

### Efficient Frontier

The efficient frontier represents the set of optimal portfolios that offer the highest expected return for a defined level of risk. Portfolios that lie below the efficient frontier are sub-optimal because they do not provide enough return for the level of risk they carry.

### Sharpe Ratio

The Sharpe ratio measures the performance of an investment compared to a risk-free asset, after adjusting for its risk. It is calculated as:

```
Sharpe Ratio = (Portfolio Return - Risk-Free Rate) / Portfolio Volatility
```

## Usage

### Basic Portfolio Analysis

```python
from src.analysis.portfolio import analyze_portfolio

# Define your portfolio
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
weights = [0.3, 0.25, 0.2, 0.15, 0.1]  # Must sum to 1.0

# Analyze the portfolio
results = analyze_portfolio(tickers, weights)

# Access results
current_stats = results['current_portfolio']['stats']
optimal_allocation = results['optimal_portfolio']['allocation']
recommendations = results['recommendations']
```

### Using the PortfolioOptimizer Class

```python
from src.analysis.portfolio import PortfolioOptimizer

# Initialize optimizer
optimizer = PortfolioOptimizer(['AAPL', 'MSFT', 'GOOGL'])

# Calculate portfolio statistics
weights = [0.4, 0.35, 0.25]
stats = optimizer.portfolio_stats(weights)

# Find optimal allocation
optimal_weights = optimizer.optimize_portfolio('max_sharpe')

# Generate efficient frontier
frontier = optimizer.generate_efficient_frontier(100)
```

### Web API Usage

The module includes a Flask web application that provides RESTful API endpoints:

#### Analyze Portfolio
```bash
POST /api/analyze
Content-Type: application/json

{
  "tickers": ["AAPL", "MSFT", "GOOGL"],
  "weights": [0.4, 0.35, 0.25]
}
```

#### Optimize Portfolio
```bash
POST /api/optimize
Content-Type: application/json

{
  "tickers": ["AAPL", "MSFT", "GOOGL"],
  "constraint": "max_sharpe"  # or "min_volatility"
}
```

#### Get Recommendations
```bash
POST /api/recommendations
Content-Type: application/json

{
  "tickers": ["AAPL", "MSFT"],
  "weights": [0.6, 0.4]
}
```

## API Reference

### PortfolioOptimizer Class

#### `__init__(tickers, start_date=None, end_date=None)`
Initialize the optimizer with stock tickers and optional date range.

**Parameters:**
- `tickers` (list): List of stock ticker symbols
- `start_date` (datetime): Start date for historical data (default: 2 years ago)
- `end_date` (datetime): End date for historical data (default: today)

#### `portfolio_stats(weights)`
Calculate portfolio statistics for given weights.

**Parameters:**
- `weights` (array): Portfolio weights (must sum to 1.0)

**Returns:**
- `dict`: Dictionary containing return, volatility, and Sharpe ratio

#### `optimize_portfolio(constraint='max_sharpe')`
Find optimal portfolio weights.

**Parameters:**
- `constraint` (str): Optimization constraint ('max_sharpe' or 'min_volatility')

**Returns:**
- `array`: Optimal portfolio weights

#### `generate_efficient_frontier(num_portfolios=100)`
Generate points along the efficient frontier.

**Parameters:**
- `num_portfolios` (int): Number of portfolios to generate

**Returns:**
- `list`: List of portfolio dictionaries with return, volatility, and weights

### Functions

#### `analyze_portfolio(tickers, weights)`
Main function for comprehensive portfolio analysis.

**Parameters:**
- `tickers` (list): List of stock tickers
- `weights` (list): Portfolio weights

**Returns:**
- `dict`: Complete analysis including current stats, optimal allocation, and recommendations

#### `get_sector_etfs()`
Get dictionary of sector ETFs for diversification.

**Returns:**
- `dict`: Dictionary mapping ETF tickers to sector names

## Example Results

### Portfolio Analysis Output

```json
{
  "current_portfolio": {
    "tickers": ["AAPL", "MSFT", "GOOGL"],
    "weights": [0.4, 0.35, 0.25],
    "stats": {
      "return": 0.15,
      "volatility": 0.18,
      "sharpe_ratio": 0.83
    }
  },
  "optimal_portfolio": {
    "weights": [0.45, 0.30, 0.25],
    "stats": {
      "return": 0.16,
      "volatility": 0.17,
      "sharpe_ratio": 0.94
    },
    "allocation": {
      "AAPL": 0.45,
      "MSFT": 0.30,
      "GOOGL": 0.25
    }
  },
  "efficient_frontier": [...],
  "recommendations": [
    {
      "ticker": "XLV",
      "name": "Healthcare",
      "sharpe_improvement": 0.12,
      "new_return": 0.14,
      "new_volatility": 0.16
    }
  ],
  "analysis": {
    "distance_from_optimal": 0.11,
    "risk_level": "Medium",
    "expected_annual_return": "15.00%",
    "annual_volatility": "18.00%"
  }
}
```

## Risk Considerations

1. **Historical Data**: The optimizer uses historical price data, which may not predict future performance
2. **Market Conditions**: Optimal allocations may change with market conditions
3. **Transaction Costs**: The model doesn't account for trading fees and taxes
4. **Liquidity**: Some assets may be difficult to trade at optimal weights
5. **Correlation Changes**: Asset correlations can change over time

## Best Practices

1. **Regular Rebalancing**: Rebalance portfolios periodically to maintain optimal allocations
2. **Diversification**: Don't rely solely on optimization - ensure adequate diversification
3. **Risk Tolerance**: Consider your personal risk tolerance when interpreting results
4. **Multiple Timeframes**: Test optimization results across different time periods
5. **Stress Testing**: Consider how portfolios perform in different market scenarios

## Deployment

### Local Development

1. Install dependencies:
   ```bash
   pip install -r web_app/requirements.txt
   ```

2. Run the web application:
   ```bash
   python web_app/app.py
   ```

3. Run the demo script:
   ```bash
   python scripts/portfolio_optimizer_demo.py
   ```

### Render Deployment

The project includes a `render.yaml` file for automatic deployment to Render:

1. Push your code to GitHub
2. Connect your repository to Render
3. Render will automatically deploy both the API and any frontend services

## Troubleshooting

### Common Issues

1. **Data Fetching Errors**: Ensure all ticker symbols are valid and Yahoo Finance is accessible
2. **Optimization Failures**: Check that weights are positive numbers and sum to 1.0
3. **Memory Issues**: Reduce the number of portfolios generated for large asset sets
4. **API Errors**: Verify that all required parameters are provided in API requests

### Performance Tips

1. **Caching**: Cache historical data to avoid repeated downloads
2. **Parallel Processing**: Use multiprocessing for large-scale optimizations
3. **Data Preprocessing**: Clean and validate data before optimization
4. **Efficient Algorithms**: Use appropriate optimization algorithms for your constraints

## Future Enhancements

- [ ] Monte Carlo simulation for retirement planning
- [ ] Risk tolerance questionnaire integration
- [ ] Transaction cost modeling
- [ ] Real-time price updates via WebSocket
- [ ] Support for cryptocurrency assets
- [ ] Export portfolio reports as PDF
- [ ] Backtesting framework integration
- [ ] Machine learning-based optimization
