"""
Configuration settings for Finance Analytics Project
"""

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
INPUTS_DIR = DATA_DIR / "inputs"
OUTPUTS_DIR = DATA_DIR / "outputs"
PROCESSED_DIR = DATA_DIR / "processed"
RAW_DIR = DATA_DIR / "raw"

# Market data directories
MARKET_DATA_DIR = INPUTS_DIR / "market_data"
FUNDAMENTAL_DATA_DIR = INPUTS_DIR / "fundamental_data"
TECHNICAL_DATA_DIR = INPUTS_DIR / "technical_data"
PORTFOLIO_DATA_DIR = INPUTS_DIR / "portfolio_data"

# Output directories
ANALYSIS_REPORTS_DIR = OUTPUTS_DIR / "analysis_reports"
BACKTEST_RESULTS_DIR = OUTPUTS_DIR / "backtest_results"
PORTFOLIO_ANALYSIS_DIR = OUTPUTS_DIR / "portfolio_analysis"
RISK_ANALYSIS_DIR = OUTPUTS_DIR / "risk_analysis"

# API Configuration
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
QUANDL_API_KEY = os.getenv("QUANDL_API_KEY")
YAHOO_FINANCE_ENABLED = True

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///finance_analytics.db")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = PROJECT_ROOT / "logs" / "finance_analytics.log"

# Create directories if they don't exist
for directory in [DATA_DIR, INPUTS_DIR, OUTPUTS_DIR, PROCESSED_DIR, RAW_DIR,
                  MARKET_DATA_DIR, FUNDAMENTAL_DATA_DIR, TECHNICAL_DATA_DIR, PORTFOLIO_DATA_DIR,
                  ANALYSIS_REPORTS_DIR, BACKTEST_RESULTS_DIR, PORTFOLIO_ANALYSIS_DIR, RISK_ANALYSIS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
