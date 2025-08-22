# 📊 Finance Analytics - Portfolio Optimizer

A comprehensive financial analytics platform featuring advanced portfolio optimization using Modern Portfolio Theory (MPT), efficient frontier analysis, and real-time market data integration.

## 🚀 Live Demo

**🌐 Web Application**: [Portfolio Optimizer](https://portfolio-optimizer.onrender.com)

## 🏗️ Project Overview

This project provides a complete financial analytics solution with:

- **Portfolio Analysis**: Analyze current portfolio performance with inflation-adjusted returns
- **Portfolio Optimization**: Find optimal allocations using Modern Portfolio Theory
- **Efficient Frontier Visualization**: Interactive plots showing risk-return relationships
- **Sector Recommendations**: Diversification suggestions with performance impact analysis
- **Real-time Market Data**: Live stock data via Yahoo Finance API
- **Modular Architecture**: Clean, maintainable codebase

## 📁 Project Structure

```
finance-analytics/
├── 📊 web_app/                    # Web Application
│   ├── app.py                     # Original monolithic app (legacy)
│   ├── app_new.py                 # Modular development version
│   ├── app_production.py          # Production version for Render
│   ├── routes.py                  # API route handlers
│   ├── templates/                 # HTML templates
│   │   └── index.html            # Main application interface
│   ├── static/                   # Static assets
│   │   ├── css/
│   │   │   └── style.css         # Application styles
│   │   └── js/
│   │       └── app.js            # Frontend JavaScript
│   └── requirements.txt          # Python dependencies
├── 🔧 src/                       # Core Analytics Engine
│   ├── analysis/                 # Analysis modules
│   │   ├── portfolio/           # Portfolio optimization
│   │   ├── fundamental/         # Fundamental analysis
│   │   ├── technical/           # Technical analysis
│   │   └── risk/                # Risk management
│   ├── data_collection/         # Data collection modules
│   ├── backtesting/             # Backtesting framework
│   ├── utils/                   # Utility functions
│   └── visualization/           # Visualization tools
├── 📈 notebooks/                # Jupyter notebooks
├── 📚 docs/                     # Documentation
├── 🧪 scripts/                  # Utility scripts
├── 📋 requirements.txt          # Main dependencies
├── 🐍 pyproject.toml           # Project configuration
└── 🚀 render.yaml              # Render deployment config
```

## 🚀 Quick Start

### Option 1: Use the Web Application (Recommended)

1. **Visit the Live Demo**: [Portfolio Optimizer](https://portfolio-optimizer.onrender.com)
2. **Enter your portfolio**: Add stock tickers and weights/dollar amounts
3. **Analyze**: Get instant portfolio analysis and optimization recommendations

### Option 2: Run Locally

```bash
# Clone the repository
git clone https://github.com/yourusername/finance-analytics.git
cd finance-analytics

# Install dependencies
pip install -r requirements.txt

# Start the web application
cd web_app
python app_new.py

# Open in browser: http://127.0.0.1:5000
```

## 🎯 Key Features

### 📊 Portfolio Analysis
- **Current Performance**: Real-time analysis of your portfolio
- **Inflation-Adjusted Returns**: Both nominal and real return calculations
- **Risk Assessment**: Volatility, Sharpe ratio, and risk categorization
- **Correlation Analysis**: Understanding asset relationships

### 🎯 Portfolio Optimization
- **Modern Portfolio Theory**: Scientific optimization using MPT
- **Multiple Strategies**: Maximum Sharpe ratio or minimum volatility
- **Custom Constraints**: Flexible minimum exposure requirements
- **Alternative Allocations**: Diversified options with performance trade-offs

### 📈 Visual Analytics
- **Efficient Frontier**: Interactive risk-return visualization
- **Capital Allocation Line**: Risk-free rate integration
- **Portfolio Positioning**: Current vs. optimal portfolio comparison
- **Performance Metrics**: Comprehensive statistical analysis

### 🔄 Real-time Data
- **Live Market Data**: Yahoo Finance integration
- **Historical Analysis**: 1-10 year customizable time periods
- **Sector Recommendations**: ETF-based diversification suggestions
- **Performance Tracking**: Continuous portfolio monitoring

## 🛠️ Technology Stack

### Backend
- **Python 3.9+**: Core programming language
- **Flask**: Web framework for API and frontend
- **NumPy/SciPy**: Numerical computations and optimization
- **yfinance**: Real-time market data
- **Plotly**: Interactive visualizations

### Frontend
- **HTML5/CSS3**: Modern, responsive interface
- **JavaScript (ES6+)**: Dynamic user interactions
- **Plotly.js**: Interactive charts and graphs
- **Bootstrap-inspired**: Clean, professional styling

### Deployment
- **Render**: Cloud hosting platform
- **GitHub**: Version control and CI/CD
- **Docker-ready**: Containerized deployment support

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main application interface |
| `/api/health` | GET | Health check |
| `/api/analyze` | POST | Portfolio analysis |
| `/api/optimize` | POST | Portfolio optimization |
| `/api/sectors` | GET | Sector recommendations |

### Example API Usage

```python
import requests

# Analyze portfolio
response = requests.post('https://portfolio-optimizer.onrender.com/api/analyze', 
    json={
        'tickers': ['AAPL', 'MSFT', 'GOOGL'],
        'weights': [0.4, 0.3, 0.3],
        'time_period': 2
    }
)

# Optimize portfolio
response = requests.post('https://portfolio-optimizer.onrender.com/api/optimize',
    json={
        'tickers': ['AAPL', 'MSFT', 'GOOGL'],
        'constraint': 'max_sharpe',
        'current_weights': [0.4, 0.3, 0.3],
        'time_period': 2,
        'min_exposure': 0.01
    }
)
```

## 🎨 User Interface Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Collapsible Sections**: Organized, user-friendly interface
- **Progress Indicators**: Visual feedback during analysis
- **Interactive Charts**: Zoom, pan, and hover interactions
- **Tab Navigation**: Easy switching between analysis and help
- **Error Handling**: Clear error messages and validation

## 🔒 Security & Privacy

- **No Data Storage**: All calculations performed in memory
- **Input Validation**: Comprehensive validation of user inputs
- **CORS Configuration**: Proper cross-origin resource sharing
- **Error Handling**: Graceful error handling without exposing internals
- **HTTPS**: Secure connections for all data transmission

## 📈 Performance Metrics

The application provides comprehensive portfolio metrics:

- **Expected Return**: Annualized expected return based on historical data
- **Volatility**: Annualized standard deviation of returns
- **Sharpe Ratio**: Risk-adjusted return measure
- **Real Return**: Inflation-adjusted return
- **Correlation Matrix**: Asset correlation analysis
- **Risk Level**: Categorized risk assessment

## 🚀 Deployment

### Render Deployment

The application is automatically deployed to Render using the `render.yaml` configuration:

1. **Connect GitHub**: Link your repository to Render
2. **Auto-deploy**: Changes to main branch trigger automatic deployment
3. **Environment Variables**: Configured for production environment
4. **SSL Certificate**: Automatic HTTPS certificate generation

### Local Development

```bash
# Development server
cd web_app
python app_new.py

# Production server
cd web_app
python app_production.py
```

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines

- **Code Style**: Follow PEP 8 Python style guide
- **Documentation**: Add docstrings and comments
- **Testing**: Include tests for new features
- **Modular Design**: Follow the existing modular architecture

## 📚 Documentation

- **User Guide**: Comprehensive help section in the web app
- **API Documentation**: Detailed endpoint documentation
- **Technical Docs**: Architecture and implementation details
- **Tutorials**: Step-by-step usage examples

## 🎯 Roadmap

### Planned Features
- **User Authentication**: Individual portfolio tracking
- **Database Integration**: Historical portfolio storage
- **Real-time Alerts**: Portfolio rebalancing notifications
- **Advanced Analytics**: Factor analysis and risk decomposition
- **Mobile App**: Native mobile application
- **API Rate Limiting**: Enhanced API management
- **Multi-currency Support**: International portfolio analysis

### Performance Improvements
- **Caching**: Redis-based caching for market data
- **CDN Integration**: Static asset optimization
- **Database Optimization**: Efficient data storage and retrieval
- **API Optimization**: Reduced response times

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Yahoo Finance**: Market data provider
- **Modern Portfolio Theory**: Harry Markowitz's foundational work
- **Flask Community**: Web framework and ecosystem
- **Open Source Contributors**: All contributors to this project

## 📞 Support

- **Issues**: Report bugs and request features on GitHub
- **Documentation**: Check the help section in the web app
- **Email**: Contact for business inquiries

---

**⭐ Star this repository if you find it helpful!**

**🔗 Live Demo**: [Portfolio Optimizer](https://portfolio-optimizer.onrender.com)
