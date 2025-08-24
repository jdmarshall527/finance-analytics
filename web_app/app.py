# web_app/app.py - Flask Web API for Portfolio Optimization
import numpy as np
import pandas as pd
import yfinance as yf
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime, timedelta
from scipy.optimize import minimize
import warnings
import sys
import os

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.analysis.portfolio import PortfolioOptimizer, analyze_portfolio, analyze_portfolio_with_period, get_sector_etfs, BlackLittermanModel, analyze_portfolio_black_litterman, get_data_manager
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)

# HTML template for the frontend
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Portfolio Optimizer</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }
        .content {
            padding: 40px;
        }
        .section {
            margin-bottom: 40px;
            padding: 25px;
            border: 1px solid #e1e8ed;
            border-radius: 10px;
            background: #f8f9fa;
        }
        .section h2 {
            color: #2c3e50;
            margin-top: 0;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #34495e;
        }
        input[type="text"], input[type="number"], select {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus, input[type="number"]:focus, select:focus {
            border-color: #3498db;
            outline: none;
        }
        button {
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        .button-group {
            display: flex;
            gap: 15px;
            margin-top: 20px;
        }
        .analyze-btn {
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        }
        .optimize-btn {
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        }
        .tab-navigation {
            display: flex;
            margin-bottom: 20px;
            border-bottom: 2px solid #e1e8ed;
        }
        .tab-button {
            background: #f8f9fa;
            border: none;
            padding: 15px 25px;
            margin-right: 5px;
            border-radius: 8px 8px 0 0;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            color: #6c757d;
            transition: all 0.3s ease;
        }
        .tab-button:hover {
            background: #e9ecef;
            color: #495057;
        }
        .tab-button.active {
            background: white;
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .help-section h3 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-top: 30px;
            margin-bottom: 20px;
        }
        .help-section h4 {
            color: #34495e;
            margin-top: 25px;
            margin-bottom: 15px;
        }
        .help-section ul {
            margin-left: 20px;
            margin-bottom: 20px;
        }
        .help-section li {
            margin-bottom: 8px;
            line-height: 1.6;
        }
        .help-section p {
            line-height: 1.6;
            margin-bottom: 15px;
        }
        .progress-container {
            display: none;
            margin: 20px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #e1e8ed;
        }
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 10px;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            width: 0%;
            transition: width 0.3s ease;
            border-radius: 10px;
        }
        .progress-text {
            text-align: center;
            color: #2c3e50;
            font-weight: 600;
        }
        .results {
            margin-top: 20px;
            padding: 20px;
            background: white;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }
        .error {
            color: #e74c3c;
            background: #fdf2f2;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #e74c3c;
        }
        .success {
            color: #27ae60;
            background: #f0f9f0;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #27ae60;
        }
        .ticker-input {
            display: flex;
            gap: 10px;
            align-items: center;
            margin-bottom: 10px;
        }
        .ticker-input input {
            flex: 1;
        }
        .ticker-input button {
            padding: 8px 15px;
            background: #e74c3c;
        }
        .api-status {
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .collapsible-header {
            background: #3498db;
            color: white;
            cursor: pointer;
            padding: 15px 20px;
            border: none;
            text-align: left;
            outline: none;
            font-size: 18px;
            font-weight: bold;
            border-radius: 8px 8px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background-color 0.3s;
            width: 100%;
        }
        
        .collapsible-header:hover {
            background: #2980b9;
        }
        
        .collapsible-header.active {
            background: #2980b9;
        }
        
        .collapsible-content {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease-out;
            background: white;
            border-radius: 0 0 8px 8px;
            border: 1px solid #ddd;
            border-top: none;
        }
        
        .collapsible-content.show {
            max-height: none;
        }
        
        .section-content {
            padding: 20px;
        }
        
        .toggle-icon {
            transition: transform 0.3s;
        }
        
        .toggle-icon.rotated {
            transform: rotate(180deg);
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-healthy {
            background: #27ae60;
        }
        .status-error {
            background: #e74c3c;
        }
        #efficientFrontierPlot, #optimizationFrontierPlot {
            width: 100%;
            height: 500px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Portfolio Optimizer</h1>
            <p>Advanced portfolio analysis and optimization using modern financial techniques</p>
        </div>
        
        <div class="content">
            <div class="api-status" id="apiStatus">
                <span class="status-indicator status-error"></span>
                <span>Checking API status...</span>
            </div>
            
            <!-- Tab Navigation -->
            <div class="tab-navigation">
                <button class="tab-button active" onclick="showTab('mpt')">📊 Modern Portfolio Theory</button>
                <button class="tab-button" onclick="showTab('blacklitterman')">🎯 Black-Litterman Model</button>
                <button class="tab-button" onclick="showTab('readme')">📖 README</button>
            </div>
            
            <!-- Modern Portfolio Theory Tab -->
            <div id="mpt-tab" class="tab-content active">
                <div class="section">
                    <h2>📊 Portfolio Input</h2>
                <div class="form-group">
                    <label for="tickers">Stock Tickers (comma-separated):</label>
                    <input type="text" id="tickers" placeholder="AAPL, MSFT, GOOGL, AMZN, TSLA" value="AAPL, MSFT, GOOGL, AMZN, TSLA">
                </div>
                <div class="form-group">
                    <label for="inputType">Input Type:</label>
                    <select id="inputType" onchange="toggleInputType()">
                        <option value="weights">Weights (must sum to 1)</option>
                        <option value="dollars">Dollar Amounts</option>
                    </select>
                </div>
                <div class="form-group" id="weightsGroup">
                    <label for="weights">Weights (comma-separated, must sum to 1):</label>
                    <input type="text" id="weights" placeholder="0.2, 0.2, 0.2, 0.2, 0.2" value="0.2, 0.2, 0.2, 0.2, 0.2">
                </div>
                <div class="form-group" id="dollarsGroup" style="display: none;">
                    <label for="dollars">Dollar Amounts (comma-separated):</label>
                    <input type="text" id="dollars" placeholder="20000, 20000, 20000, 20000, 20000" value="20000, 20000, 20000, 20000, 20000">
                </div>
                <div class="form-group">
                    <label for="timePeriod">Analysis Time Period:</label>
                    <select id="timePeriod">
                        <option value="1">1 Year</option>
                        <option value="2" selected>2 Years</option>
                        <option value="3">3 Years</option>
                        <option value="4">4 Years</option>
                        <option value="5">5 Years</option>
                        <option value="6">6 Years</option>
                        <option value="7">7 Years</option>
                        <option value="8">8 Years</option>
                        <option value="9">9 Years</option>
                        <option value="10">10 Years</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="constraint">Optimization Strategy (for optimization only):</label>
                    <select id="constraint">
                        <option value="max_sharpe">Maximum Sharpe Ratio</option>
                        <option value="min_volatility">Minimum Volatility</option>
                    </select>
                </div>
                <div class="button-group">
                    <button onclick="analyzePortfolio()" class="analyze-btn">🔍 Analyze Portfolio</button>
                </div>
                
                <div class="progress-container" id="progressContainer">
                    <div class="progress-text" id="progressText">Initializing analysis...</div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill"></div>
                    </div>
                </div>
            </div>
            
            <div class="section" id="analysisSection" style="display: none;">
                <button class="collapsible-header" onclick="toggleSection('analysisSection')">
                    📈 Analysis Results
                    <span class="toggle-icon">▼</span>
                </button>
                <div class="collapsible-content show">
                    <div class="section-content">
                        <div id="analysisResults"></div>
                    </div>
                </div>
            </div>
            
            <div class="section" id="optimizationSection">
                <button class="collapsible-header" onclick="toggleSection('optimizationSection')">
                    🎯 Optimization Results
                    <span class="toggle-icon">▼</span>
                </button>
                <div class="collapsible-content show">
                    <div class="section-content">
                        <div class="form-group" style="margin-bottom: 20px;">
                            <label for="minExposure">Minimum Exposure per Security (%):</label>
                            <input type="text" id="minExposure" placeholder="1.0 or 1.0, 2.0, 1.5 (leave blank for 1% default)" value="">
                            <small>Enter one number for all securities, or separate values for each security (comma-separated). Leave blank for 1% default.</small>
                        </div>
                        <div style="margin-bottom: 20px;">
                            <button onclick="optimizePortfolio()" class="optimize-btn">⚡ Optimize Portfolio</button>
                        </div>
                        <div id="optimizationResults"></div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <button class="collapsible-header" onclick="toggleSection('sectorSection')">
                    📈 Sector Recommendations
                    <span class="toggle-icon">▼</span>
                </button>
                <div class="collapsible-content show" id="sectorSection">
                    <div class="section-content">
                        <button onclick="getSectors()">Get Available Sectors</button>
                        <div id="sectorResults"></div>
                    </div>
                </div>
            </div>
            </div>
            
            <!-- Black-Litterman Model Tab -->
            <div id="blacklitterman-tab" class="tab-content">
                <div class="section">
                    <h2>🎯 Black-Litterman Model</h2>
                    <p>The Black-Litterman model combines market equilibrium returns with your personal views to create more stable and intuitive portfolio allocations.</p>
                    
                    <div class="form-group">
                        <label for="bl-tickers">Stock Tickers (comma-separated):</label>
                        <input type="text" id="bl-tickers" placeholder="AAPL, MSFT, GOOGL, AMZN, TSLA" value="AAPL, MSFT, GOOGL, AMZN, TSLA">
                    </div>
                    
                    <div class="form-group">
                        <label for="bl-inputType">Input Type:</label>
                        <select id="bl-inputType" onchange="toggleBLInputType()">
                            <option value="weights">Weights (must sum to 1)</option>
                            <option value="dollars">Dollar Amounts</option>
                        </select>
                    </div>
                    
                    <div class="form-group" id="bl-weightsGroup">
                        <label for="bl-weights">Weights (comma-separated, must sum to 1):</label>
                        <input type="text" id="bl-weights" placeholder="0.2, 0.2, 0.2, 0.2, 0.2" value="0.2, 0.2, 0.2, 0.2, 0.2">
                    </div>
                    
                    <div class="form-group" id="bl-dollarsGroup" style="display: none;">
                        <label for="bl-dollars">Dollar Amounts (comma-separated):</label>
                        <input type="text" id="bl-dollars" placeholder="20000, 20000, 20000, 20000, 20000" value="20000, 20000, 20000, 20000, 20000">
                    </div>
                    
                    <div class="form-group">
                        <label for="bl-timePeriod">Analysis Time Period:</label>
                        <select id="bl-timePeriod">
                            <option value="1">1 Year</option>
                            <option value="2" selected>2 Years</option>
                            <option value="3">3 Years</option>
                            <option value="4">4 Years</option>
                            <option value="5">5 Years</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="bl-riskFreeRate">Risk-Free Rate (%):</label>
                        <input type="number" id="bl-riskFreeRate" placeholder="2.0" value="2.0" step="0.1" min="0" max="10">
                    </div>
                    
                    <div class="section">
                        <h3>📝 Investor Views (Optional)</h3>
                        <p>Add your personal views about expected returns. Leave empty to use market equilibrium only.</p>
                        
                        <div id="views-container">
                            <div class="view-entry">
                                <div class="form-group">
                                    <label>View Type:</label>
                                    <select class="view-type">
                                        <option value="absolute">Absolute Return</option>
                                        <option value="relative">Relative Return</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>Assets:</label>
                                    <input type="text" class="view-assets" placeholder="AAPL, MSFT">
                                </div>
                                <div class="form-group">
                                    <label>Expected Return (%):</label>
                                    <input type="number" class="view-return" placeholder="15.0" step="0.1">
                                </div>
                                <div class="form-group">
                                    <label>Confidence (0-1):</label>
                                    <input type="number" class="view-confidence" placeholder="0.7" step="0.1" min="0" max="1">
                                </div>
                                <button type="button" onclick="removeView(this)" style="background: #e74c3c;">Remove View</button>
                            </div>
                        </div>
                        
                        <button type="button" onclick="addView()" style="background: #27ae60;">Add View</button>
                    </div>
                    
                    <div class="button-group">
                        <button onclick="analyzeBlackLitterman()" class="analyze-btn">🔍 Analyze with Black-Litterman</button>
                    </div>
                    
                    <div class="progress-container" id="bl-progressContainer">
                        <div class="progress-text" id="bl-progressText">Initializing analysis...</div>
                        <div class="progress-bar">
                            <div class="progress-fill" id="bl-progressFill"></div>
                        </div>
                    </div>
                </div>
                
                <div class="section" id="bl-analysisSection" style="display: none;">
                    <button class="collapsible-header" onclick="toggleSection('bl-analysisSection')">
                        📈 Black-Litterman Results
                        <span class="toggle-icon">▼</span>
                    </button>
                    <div class="collapsible-content show">
                        <div class="section-content">
                            <div id="bl-analysisResults"></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- README Tab -->
            <div id="readme-tab" class="tab-content">
                <div class="section help-section">
                    <h2>📖 Help & Documentation</h2>
                    
                    <h3>🎯 Portfolio Optimization Models</h3>
                    
                    <h4>Modern Portfolio Theory (MPT)</h4>
                    <p>Modern Portfolio Theory uses historical data to find the best allocation of assets that maximizes returns for a given level of risk, or minimizes risk for a given level of return. It's based on the principle that an investment's risk and return should not be assessed individually, but by how it contributes to a portfolio's overall risk and return.</p>
                    
                    <h4>Black-Litterman Model</h4>
                    <p>The Black-Litterman model combines market equilibrium returns with your personal views to create more stable and intuitive portfolio allocations. It addresses some limitations of traditional MPT by incorporating investor insights and market equilibrium, resulting in more realistic and diversified portfolios.</p>
                    
                    <h3>📊 Input Fields Explained</h3>
                    
                    <h4>Modern Portfolio Theory (MPT) Tab</h4>
                    
                    <h4>Stock Tickers</h4>
                    <ul>
                        <li><strong>Format:</strong> Enter stock symbols separated by commas (e.g., AAPL, MSFT, GOOGL)</li>
                        <li><strong>Examples:</strong> AAPL (Apple), MSFT (Microsoft), GOOGL (Alphabet), AMZN (Amazon), TSLA (Tesla)</li>
                        <li><strong>Note:</strong> Use standard stock symbols as they appear on major exchanges</li>
                    </ul>
                    
                    <h4>Input Type</h4>
                    <ul>
                        <li><strong>Weights:</strong> Enter portfolio weights as decimals that sum to 1 (e.g., 0.3, 0.3, 0.4)</li>
                        <li><strong>Dollar Amounts:</strong> Enter actual dollar amounts invested in each stock (e.g., 30000, 30000, 40000)</li>
                        <li><strong>Auto-conversion:</strong> Dollar amounts are automatically converted to weights</li>
                    </ul>
                    
                    <h4>Analysis Time Period</h4>
                    <ul>
                        <li><strong>Range:</strong> 1-10 years of historical data</li>
                        <li><strong>Default:</strong> 2 years (balanced between recent trends and statistical significance)</li>
                        <li><strong>Shorter periods (1-3 years):</strong> More responsive to recent market conditions</li>
                        <li><strong>Longer periods (5-10 years):</strong> More stable, captures longer-term trends</li>
                    </ul>
                    
                    <h4>Minimum Exposure per Security</h4>
                    <ul>
                        <li><strong>Default:</strong> 1% for all securities (if left blank)</li>
                        <li><strong>Single value:</strong> Enter one number (e.g., "2.0") to apply to all securities</li>
                        <li><strong>Individual values:</strong> Enter comma-separated values (e.g., "1.0, 2.0, 1.5") for each security</li>
                        <li><strong>Purpose:</strong> Ensures diversification by preventing 0% allocations in alternative optimization</li>
                        <li><strong>Example:</strong> "2.0" means each security gets at least 2% allocation</li>
                    </ul>
                    
                    <h4>Optimization Strategy</h4>
                    <ul>
                        <li><strong>Maximum Sharpe Ratio:</strong> Finds the portfolio with the best risk-adjusted returns</li>
                        <li><strong>Minimum Volatility:</strong> Finds the portfolio with the lowest risk (volatility)</li>
                    </ul>
                    
                    <h4>Black-Litterman Model Tab</h4>
                    
                    <h4>Risk-Free Rate</h4>
                    <ul>
                        <li><strong>Default:</strong> 2.0% (current market rate)</li>
                        <li><strong>Purpose:</strong> Used as the baseline return for calculating excess returns and Sharpe ratios</li>
                        <li><strong>Adjustment:</strong> Can be modified based on current market conditions</li>
                    </ul>
                    
                    <h4>Investor Views</h4>
                    <ul>
                        <li><strong>Absolute Views:</strong> Specify expected return for specific assets (e.g., "AAPL will return 15%")</li>
                        <li><strong>Relative Views:</strong> Specify relative performance between assets (e.g., "AAPL will outperform MSFT by 2%")</li>
                        <li><strong>Confidence:</strong> Express your confidence in each view (0-1 scale, where 1 is highest confidence)</li>
                        <li><strong>Optional:</strong> Leave empty to use market equilibrium returns only</li>
                    </ul>
                    
                    <h4>View Examples</h4>
                    <ul>
                        <li><strong>Absolute:</strong> "I expect AAPL to return 15% annually" → Type: Absolute, Assets: AAPL, Return: 15%, Confidence: 0.8</li>
                        <li><strong>Relative:</strong> "I expect AAPL to outperform MSFT by 3%" → Type: Relative, Assets: AAPL, MSFT, Return: 3%, Confidence: 0.7</li>
                    </ul>
                    
                    <h3>📈 Understanding the Results</h3>
                    
                    <h4>Portfolio Performance Metrics</h4>
                    <ul>
                        <li><strong>Nominal Return:</strong> Annualized expected return based on historical data (not adjusted for inflation)</li>
                        <li><strong>Real Return:</strong> Inflation-adjusted return showing actual purchasing power growth</li>
                        <li><strong>Volatility:</strong> Annualized standard deviation of returns (measure of risk)</li>
                        <li><strong>Sharpe Ratio:</strong> Risk-adjusted return using nominal returns (higher is better, above 1.0 is good)</li>
                        <li><strong>Real Sharpe Ratio:</strong> Risk-adjusted return using inflation-adjusted returns</li>
                        <li><strong>Inflation Rate:</strong> Current annual inflation rate used for calculations (default 2.5%)</li>
                        <li><strong>Risk Level:</strong> Categorized risk (Low: <15%, Medium: 15-25%, High: >25%)</li>
                    </ul>
                    
                    <h4>Optimal Allocation</h4>
                    <ul>
                        <li>Shows the recommended percentage allocation for each stock</li>
                        <li>Based on historical performance and correlation between stocks</li>
                        <li>Designed to maximize the chosen objective (Sharpe ratio or minimize volatility)</li>
                    </ul>
                    
                    <h4>Diversification Recommendations</h4>
                    <ul>
                        <li><strong>Expected Return:</strong> New portfolio return if you add 10% of this sector</li>
                        <li><strong>Volatility:</strong> New portfolio risk level (lower is better for risk reduction)</li>
                        <li><strong>Sharpe Ratio:</strong> Risk-adjusted return of the enhanced portfolio (higher is better)</li>
                        <li><strong>Correlation:</strong> How closely this sector moves with your current holdings (lower is better for diversification)</li>
                        <li><strong>Color Coding:</strong> Green for improvements, red for potential drawbacks</li>
                        <li><strong>Impact:</strong> Shows that adding 10% of the recommended sector would improve your portfolio</li>
                    </ul>
                    
                    <h3>📊 Efficient Frontier Graph Explained</h3>
                    
                    <h4>Graph Elements</h4>
                    <ul>
                        <li><strong>Blue Line (Efficient Frontier):</strong> Shows all optimal portfolios - maximum return for each risk level</li>
                        <li><strong>Purple Dashed Line (Capital Allocation Line):</strong> Shows combinations of the optimal risky portfolio and risk-free asset</li>
                        <li><strong>Orange Star (Tangency Portfolio):</strong> The optimal risky portfolio that maximizes Sharpe ratio</li>
                        <li><strong>Red Circle (Current Portfolio):</strong> Your current allocation position</li>
                        <li><strong>Green Diamond (Optimal Portfolio):</strong> The recommended allocation (in optimization results)</li>
                    </ul>
                    
                    <h4>How to Read the Graph</h4>
                    <ul>
                        <li><strong>X-axis (Volatility):</strong> Risk level - higher values mean more risk</li>
                        <li><strong>Y-axis (Expected Return):</strong> Annual return - higher values mean higher expected returns</li>
                        <li><strong>Position:</strong> Where your portfolio sits relative to the efficient frontier</li>
                        <li><strong>Improvement Potential:</strong> Distance between current and optimal positions</li>
                    </ul>
                    
                    <h3>🔍 MPT vs Black-Litterman Comparison</h3>
                    
                    <h4>Modern Portfolio Theory (MPT)</h4>
                    <ul>
                        <li><strong>Approach:</strong> Uses historical data to estimate expected returns and risk</li>
                        <li><strong>Strengths:</strong> Simple, well-established, good for historical analysis</li>
                        <li><strong>Limitations:</strong> Sensitive to input data, may produce extreme allocations</li>
                        <li><strong>Best for:</strong> Historical analysis, educational purposes, basic portfolio optimization</li>
                    </ul>
                    
                    <h4>Black-Litterman Model</h4>
                    <ul>
                        <li><strong>Approach:</strong> Combines market equilibrium with investor views</li>
                        <li><strong>Strengths:</strong> More stable allocations, incorporates personal insights, addresses MPT limitations</li>
                        <li><strong>Features:</strong> Market equilibrium returns, investor views, confidence levels</li>
                        <li><strong>Best for:</strong> Active portfolio management, incorporating personal views, more realistic allocations</li>
                    </ul>
                    
                    <h3>🔍 Analysis vs Optimization</h3>
                    
                    <h4>Portfolio Analysis</h4>
                    <ul>
                        <li>Analyzes your current portfolio performance</li>
                        <li>Shows how your allocation compares to optimal</li>
                        <li>Provides diversification recommendations</li>
                        <li>Displays efficient frontier with your current position</li>
                    </ul>
                    
                    <h4>Portfolio Optimization</h4>
                    <ul>
                        <li>Finds the best possible allocation for your chosen strategy</li>
                        <li>Compares current vs optimal performance</li>
                        <li>Shows specific allocation recommendations</li>
                        <li>Displays efficient frontier with both current and optimal positions</li>
                    </ul>
                    
                    <h3>💡 Tips for Best Results</h3>
                    <ul>
                        <li><strong>Diversify:</strong> Include stocks from different sectors for better risk management</li>
                        <li><strong>Time Period:</strong> Choose based on your investment horizon and market outlook</li>
                        <li><strong>Shorter periods:</strong> Use for tactical adjustments and recent market conditions</li>
                        <li><strong>Longer periods:</strong> Use for strategic allocation and long-term planning</li>
                        <li><strong>Minimum Exposure:</strong> Use higher minimums for more conservative portfolios</li>
                        <li><strong>Individual Minimums:</strong> Set higher minimums for core holdings, lower for satellite positions</li>
                        <li><strong>Regular Review:</strong> Re-optimize periodically as market conditions change</li>
                        <li><strong>Consider Costs:</strong> Factor in trading costs when implementing changes</li>
                        <li><strong>Risk Tolerance:</strong> Choose optimization strategy based on your risk preferences</li>
                    </ul>
                    
                    <h3>⚠️ Important Disclaimers</h3>
                    <ul>
                        <li>Past performance does not guarantee future results</li>
                        <li>This tool is for educational and analysis purposes only</li>
                        <li>Consider consulting with a financial advisor before making investment decisions</li>
                        <li>Market conditions can change rapidly, affecting optimal allocations</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Check API health on page load
        window.onload = function() {
            checkApiHealth();
        };

        function showTab(tabName) {
            // Hide all tab contents
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(content => {
                content.classList.remove('active');
            });
            
            // Remove active class from all tab buttons
            const tabButtons = document.querySelectorAll('.tab-button');
            tabButtons.forEach(button => {
                button.classList.remove('active');
            });
            
            // Show selected tab content
            document.getElementById(tabName + '-tab').classList.add('active');
            
            // Add active class to clicked button
            event.target.classList.add('active');
        }

        function toggleInputType() {
            const inputType = document.getElementById('inputType').value;
            const weightsGroup = document.getElementById('weightsGroup');
            const dollarsGroup = document.getElementById('dollarsGroup');
            
            if (inputType === 'weights') {
                weightsGroup.style.display = 'block';
                dollarsGroup.style.display = 'none';
            } else {
                weightsGroup.style.display = 'none';
                dollarsGroup.style.display = 'block';
            }
        }

        function toggleBLInputType() {
            const inputType = document.getElementById('bl-inputType').value;
            const weightsGroup = document.getElementById('bl-weightsGroup');
            const dollarsGroup = document.getElementById('bl-dollarsGroup');
            
            if (inputType === 'weights') {
                weightsGroup.style.display = 'block';
                dollarsGroup.style.display = 'none';
            } else {
                weightsGroup.style.display = 'none';
                dollarsGroup.style.display = 'block';
            }
        }

        function addView() {
            const container = document.getElementById('views-container');
            const newView = document.createElement('div');
            newView.className = 'view-entry';
            newView.style.border = '1px solid #ddd';
            newView.style.padding = '15px';
            newView.style.margin = '10px 0';
            newView.style.borderRadius = '8px';
            newView.style.backgroundColor = '#f8f9fa';
            
            newView.innerHTML = `
                <div class="form-group">
                    <label>View Type:</label>
                    <select class="view-type">
                        <option value="absolute">Absolute Return</option>
                        <option value="relative">Relative Return</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Assets:</label>
                    <input type="text" class="view-assets" placeholder="AAPL, MSFT">
                </div>
                <div class="form-group">
                    <label>Expected Return (%):</label>
                    <input type="number" class="view-return" placeholder="15.0" step="0.1">
                </div>
                <div class="form-group">
                    <label>Confidence (0-1):</label>
                    <input type="number" class="view-confidence" placeholder="0.7" step="0.1" min="0" max="1">
                </div>
                <button type="button" onclick="removeView(this)" style="background: #e74c3c;">Remove View</button>
            `;
            
            container.appendChild(newView);
        }

        function removeView(button) {
            button.parentElement.remove();
        }



        async function checkApiHealth() {
            try {
                const response = await fetch('/api/health');
                const data = await response.json();
                const statusDiv = document.getElementById('apiStatus');
                if (response.ok) {
                    statusDiv.innerHTML = '<span class="status-indicator status-healthy"></span><span>API is healthy and ready</span>';
                } else {
                    throw new Error('API not healthy');
                }
            } catch (error) {
                const statusDiv = document.getElementById('apiStatus');
                statusDiv.innerHTML = '<span class="status-indicator status-error"></span><span>API is not available</span>';
            }
        }

        async function analyzePortfolio() {
            const tickers = document.getElementById('tickers').value.split(',').map(t => t.trim());
            const inputType = document.getElementById('inputType').value;
            const timePeriod = parseInt(document.getElementById('timePeriod').value);
            
            let weights;
            if (inputType === 'weights') {
                weights = document.getElementById('weights').value.split(',').map(w => parseFloat(w.trim()));
            } else {
                const dollars = document.getElementById('dollars').value.split(',').map(d => parseFloat(d.trim()));
                const total = dollars.reduce((sum, amount) => sum + amount, 0);
                weights = dollars.map(amount => amount / total);
            }
            
            if (tickers.length !== weights.length) {
                showError('analysisResults', 'Number of tickers must match number of inputs');
                return;
            }
            
            // Parse minimum exposure
            const minExposureInput = document.getElementById('minExposure').value.trim();
            let minExposure = null;
            if (minExposureInput) {
                const exposureValues = minExposureInput.split(',').map(v => parseFloat(v.trim()) / 100); // Convert % to decimal
                if (exposureValues.length === 1) {
                    // Single value for all securities
                    minExposure = exposureValues[0];
                } else if (exposureValues.length === tickers.length) {
                    // Individual values for each security
                    minExposure = exposureValues;
                } else {
                    showError('analysisResults', 'Minimum exposure must be one number or match the number of tickers');
                    return;
                }
            }
            
            // Show progress bar
            showProgress();
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ tickers, weights, time_period: timePeriod, min_exposure: minExposure })
                });
                
                const data = await response.json();
                
                // Hide progress bar
                hideProgress();
                
                if (response.ok) {
                    showAnalysisResults(data);
                } else {
                    showError('analysisResults', data.error || 'Analysis failed');
                }
            } catch (error) {
                // Hide progress bar
                hideProgress();
                console.error('Error:', error);
                showError('analysisResults', 'Failed to connect to API: ' + error.message);
            }
        }

        async function optimizePortfolio() {
            const tickers = document.getElementById('tickers').value.split(',').map(t => t.trim());
            const constraint = document.getElementById('constraint').value;
            const inputType = document.getElementById('inputType').value;
            const timePeriod = parseInt(document.getElementById('timePeriod').value);
            
            let currentWeights;
            if (inputType === 'weights') {
                currentWeights = document.getElementById('weights').value.split(',').map(w => parseFloat(w.trim()));
            } else {
                const dollars = document.getElementById('dollars').value.split(',').map(d => parseFloat(d.trim()));
                const total = dollars.reduce((sum, amount) => sum + amount, 0);
                currentWeights = dollars.map(amount => amount / total);
            }
            
            if (tickers.length !== currentWeights.length) {
                showError('optimizationResults', 'Number of tickers must match number of inputs');
                return;
            }
            
            // Parse minimum exposure
            const minExposureInput = document.getElementById('minExposure').value.trim();
            let minExposure = null;
            if (minExposureInput) {
                const exposureValues = minExposureInput.split(',').map(v => parseFloat(v.trim()) / 100); // Convert % to decimal
                if (exposureValues.length === 1) {
                    // Single value for all securities
                    minExposure = exposureValues[0];
                } else if (exposureValues.length === tickers.length) {
                    // Individual values for each security
                    minExposure = exposureValues;
                } else {
                    showError('optimizationResults', 'Minimum exposure must be one number or match the number of tickers');
                    return;
                }
            }
            
            // Show progress bar
            showProgress();
            
            try {
                const response = await fetch('/api/optimize', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ tickers, constraint, current_weights: currentWeights, time_period: timePeriod, min_exposure: minExposure })
                });
                
                const data = await response.json();
                
                // Hide progress bar
                hideProgress();
                
                if (response.ok) {
                    showOptimizationResults(data);
                } else {
                    showError('optimizationResults', data.error || 'Optimization failed');
                }
            } catch (error) {
                // Hide progress bar
                hideProgress();
                console.error('Error:', error);
                showError('optimizationResults', 'Failed to connect to API: ' + error.message);
            }
        }

        async function getSectors() {
            try {
                const response = await fetch('/api/sectors');
                const data = await response.json();
                
                if (response.ok) {
                    showSectorResults(data);
                } else {
                    showError('sectorResults', data.error || 'Failed to get sectors');
                }
            } catch (error) {
                console.error('Error:', error);
                showError('sectorResults', 'Failed to connect to API: ' + error.message);
            }
        }

        async function analyzeBlackLitterman() {
            const tickers = document.getElementById('bl-tickers').value.split(',').map(t => t.trim());
            const inputType = document.getElementById('bl-inputType').value;
            const timePeriod = parseInt(document.getElementById('bl-timePeriod').value);
            const riskFreeRate = parseFloat(document.getElementById('bl-riskFreeRate').value) / 100;
            
            let weights;
            if (inputType === 'weights') {
                weights = document.getElementById('bl-weights').value.split(',').map(w => parseFloat(w.trim()));
            } else {
                const dollars = document.getElementById('bl-dollars').value.split(',').map(d => parseFloat(d.trim()));
                const total = dollars.reduce((sum, amount) => sum + amount, 0);
                weights = dollars.map(amount => amount / total);
            }
            
            if (tickers.length !== weights.length) {
                showError('bl-analysisResults', 'Number of tickers must match number of inputs');
                return;
            }
            
            // Collect views
            const viewEntries = document.querySelectorAll('.view-entry');
            const views = [];
            const confidences = [];
            
            for (const entry of viewEntries) {
                const viewType = entry.querySelector('.view-type').value;
                const assets = entry.querySelector('.view-assets').value.split(',').map(a => a.trim());
                const viewReturn = parseFloat(entry.querySelector('.view-return').value) / 100; // Convert % to decimal
                const confidence = parseFloat(entry.querySelector('.view-confidence').value);
                
                if (assets.length > 0 && !isNaN(viewReturn) && !isNaN(confidence)) {
                    views.push({
                        assets: assets,
                        view: viewReturn,
                        type: viewType
                    });
                    confidences.push(confidence);
                }
            }
            
            // Show progress bar
            showBLProgress();
            
            try {
                const response = await fetch('/api/blacklitterman', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        tickers, 
                        weights, 
                        time_period: timePeriod, 
                        risk_free_rate: riskFreeRate,
                        views: views.length > 0 ? views : null,
                        confidences: confidences.length > 0 ? confidences : null
                    })
                });
                
                const data = await response.json();
                
                // Hide progress bar
                hideBLProgress();
                
                if (response.ok) {
                    showBlackLittermanResults(data);
                } else {
                    showError('bl-analysisResults', data.error || 'Black-Litterman analysis failed');
                }
            } catch (error) {
                // Hide progress bar
                hideBLProgress();
                console.error('Error:', error);
                showError('bl-analysisResults', 'Failed to connect to API: ' + error.message);
            }
        }

        function showBLProgress() {
            const progressContainer = document.getElementById('bl-progressContainer');
            const progressFill = document.getElementById('bl-progressFill');
            const progressText = document.getElementById('bl-progressText');
            
            progressContainer.style.display = 'block';
            progressFill.style.width = '0%';
            progressText.textContent = 'Initializing Black-Litterman analysis...';
            
            // Simulate progress
            let progress = 0;
            const progressInterval = setInterval(() => {
                progress += Math.random() * 15;
                if (progress > 90) progress = 90;
                
                progressFill.style.width = progress + '%';
                
                if (progress < 30) {
                    progressText.textContent = 'Fetching market data...';
                } else if (progress < 60) {
                    progressText.textContent = 'Calculating equilibrium returns...';
                } else if (progress < 90) {
                    progressText.textContent = 'Incorporating investor views...';
                }
            }, 200);
            
            // Store interval ID for cleanup
            progressContainer.dataset.intervalId = progressInterval;
        }

        function hideBLProgress() {
            const progressContainer = document.getElementById('bl-progressContainer');
            const progressFill = document.getElementById('bl-progressFill');
            const progressText = document.getElementById('bl-progressText');
            
            // Complete the progress bar
            progressFill.style.width = '100%';
            progressText.textContent = 'Analysis complete!';
            
            // Clear the interval
            if (progressContainer.dataset.intervalId) {
                clearInterval(parseInt(progressContainer.dataset.intervalId));
            }
            
            // Hide after a short delay
            setTimeout(() => {
                progressContainer.style.display = 'none';
            }, 1000);
        }

        function showBlackLittermanResults(data) {
            const resultsDiv = document.getElementById('bl-analysisResults');
            const analysisSection = document.getElementById('bl-analysisSection');
            
            // Extract current portfolio stats
            const currentStats = data.current_portfolio.stats;
            const analysis = data.analysis;
            
            let viewsHtml = '';
            if (data.views_used) {
                viewsHtml = `
                    <h4>Investor Views Applied:</h4>
                    <p>Your personal views were incorporated into the analysis, combining market equilibrium with your insights.</p>
                `;
            } else {
                viewsHtml = `
                    <h4>Market Equilibrium Only:</h4>
                    <p>Analysis based on market equilibrium returns without additional investor views.</p>
                `;
            }
            
            resultsDiv.innerHTML = `
                <div class="results success">
                    <h3>Black-Litterman Analysis Results</h3>
                    <p><strong>Model Type:</strong> ${analysis.model_type}</p>
                    <p><strong>Analysis Period:</strong> ${analysis.time_period} of historical data</p>
                    <p><strong>Risk-Free Rate:</strong> ${analysis.risk_free_rate}</p>
                    ${viewsHtml}
                    
                    <h4>Current Portfolio Performance:</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 15px 0;">
                        <div style="padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #3498db;">
                            <h5 style="margin: 0 0 10px 0; color: #2c3e50;">Expected Returns</h5>
                            <p><strong>Expected Return:</strong> ${(currentStats.return * 100).toFixed(2)}%</p>
                            <p><strong>Volatility:</strong> ${(currentStats.volatility * 100).toFixed(2)}%</p>
                            <p><strong>Sharpe Ratio:</strong> ${currentStats.sharpe_ratio.toFixed(3)}</p>
                        </div>
                        <div style="padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #e74c3c;">
                            <h5 style="margin: 0 0 10px 0; color: #2c3e50;">Risk Metrics</h5>
                            <p><strong>Risk-Free Rate:</strong> ${(parseFloat(analysis.risk_free_rate.replace('%', ''))).toFixed(1)}%</p>
                            <p><strong>Excess Return:</strong> ${((currentStats.return - parseFloat(analysis.risk_free_rate.replace('%', '')) / 100) * 100).toFixed(2)}%</p>
                            <p><strong>Risk-Adjusted Return:</strong> ${currentStats.sharpe_ratio.toFixed(3)}</p>
                        </div>
                    </div>
                    
                    <h4>Optimal Portfolio (Black-Litterman):</h4>
                    <p><strong>Expected Return:</strong> ${(data.optimal_portfolio.stats.return * 100).toFixed(2)}%</p>
                    <p><strong>Volatility:</strong> ${(data.optimal_portfolio.stats.volatility * 100).toFixed(2)}%</p>
                    <p><strong>Sharpe Ratio:</strong> ${data.optimal_portfolio.stats.sharpe_ratio.toFixed(3)}</p>
                    
                    <h4>Optimal Allocation:</h4>
                    <ul>
                        ${Object.entries(data.optimal_portfolio.allocation).map(([ticker, weight]) => 
                            `<li><strong>${ticker}:</strong> ${(weight * 100).toFixed(2)}%</li>`
                        ).join('')}
                    </ul>
                    
                    ${data.equilibrium_returns ? `
                        <h4>Equilibrium Returns:</h4>
                        <ul>
                            ${data.equilibrium_returns.map((ret, idx) => 
                                `<li><strong>${data.current_portfolio.tickers[idx]}:</strong> ${(ret * 100).toFixed(2)}%</li>`
                            ).join('')}
                        </ul>
                    ` : ''}
                    
                    ${data.posterior_returns ? `
                        <h4>Posterior Returns (with views):</h4>
                        <ul>
                            ${data.posterior_returns.map((ret, idx) => 
                                `<li><strong>${data.current_portfolio.tickers[idx]}:</strong> ${(ret * 100).toFixed(2)}%</li>`
                            ).join('')}
                        </ul>
                    ` : ''}
                </div>
                
                <div class="results success">
                    <h3>Black-Litterman Efficient Frontier</h3>
                    <div id="bl-efficientFrontierPlot"></div>
                </div>
            `;
            
            // Show the analysis section
            analysisSection.style.display = 'block';
            
            // Ensure the section is expanded when showing results
            const content = analysisSection.querySelector('.collapsible-content');
            const header = analysisSection.querySelector('.collapsible-header');
            const icon = header.querySelector('.toggle-icon');
            
            content.classList.add('show');
            header.classList.add('active');
            icon.classList.add('rotated');
            
            // Create efficient frontier plot if data is available
            if (data.efficient_frontier) {
                createBLEfficientFrontierPlot(data.efficient_frontier, currentStats);
            }
        }

        function createBLEfficientFrontierPlot(frontierData, currentStats) {
            // Prepare data for plotting
            const efVolatility = frontierData.map(p => p.volatility * 100);
            const efReturns = frontierData.map(p => p.return * 100);
            
            const traces = [
                {
                    x: efVolatility,
                    y: efReturns,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Black-Litterman Efficient Frontier',
                    line: { color: '#8E44AD', width: 3 },
                    hovertemplate: 'Volatility: %{x:.2f}%<br>Return: %{y:.2f}%<extra></extra>'
                },
                {
                    x: [currentStats.volatility * 100],
                    y: [currentStats.return * 100],
                    type: 'scatter',
                    mode: 'markers',
                    name: 'Current Portfolio',
                    marker: { 
                        color: '#C73E1D', 
                        size: 12,
                        symbol: 'circle'
                    },
                    hovertemplate: 'Current Portfolio<br>Volatility: %{x:.2f}%<br>Return: %{y:.2f}%<extra></extra>'
                }
            ];
            
            const layout = {
                title: 'Black-Litterman Efficient Frontier',
                xaxis: {
                    title: 'Portfolio Volatility (%)',
                    gridcolor: '#E5E5E5'
                },
                yaxis: {
                    title: 'Expected Annual Return (%)',
                    gridcolor: '#E5E5E5'
                },
                plot_bgcolor: 'white',
                paper_bgcolor: 'white',
                font: { color: '#2C3E50' },
                legend: {
                    x: 0.02,
                    y: 0.98,
                    bgcolor: 'rgba(255,255,255,0.8)',
                    bordercolor: '#E5E5E5'
                },
                margin: { l: 60, r: 30, t: 60, b: 60 }
            };
            
            Plotly.newPlot('bl-efficientFrontierPlot', traces, layout, {
                responsive: true,
                displayModeBar: true,
                modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
            });
        }

        function showAnalysisResults(data) {
            const resultsDiv = document.getElementById('analysisResults');
            const analysisSection = document.getElementById('analysisSection');
            
            // Extract current portfolio stats
            const currentStats = data.current_portfolio.stats;
            const analysis = data.analysis;
            
            resultsDiv.innerHTML = `
                <div class="results success">
                    <h3>Portfolio Analysis Results</h3>
                    <p><strong>Analysis Period:</strong> ${analysis.time_period || '2 years'} of historical data</p>
                    <p><strong>Inflation Rate:</strong> ${(currentStats.inflation_rate * 100).toFixed(1)}% (used for real return calculations)</p>
                    <h4>Current Portfolio Performance:</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 15px 0;">
                        <div style="padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #3498db;">
                            <h5 style="margin: 0 0 10px 0; color: #2c3e50;">Nominal Returns</h5>
                            <p><strong>Expected Return:</strong> ${(currentStats.return * 100).toFixed(2)}%</p>
                            <p><strong>Volatility:</strong> ${(currentStats.volatility * 100).toFixed(2)}%</p>
                            <p><strong>Sharpe Ratio:</strong> ${currentStats.sharpe_ratio.toFixed(3)}</p>
                        </div>
                        <div style="padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #e74c3c;">
                            <h5 style="margin: 0 0 10px 0; color: #2c3e50;">Inflation-Adjusted (Real) Returns</h5>
                            <p><strong>Real Return:</strong> ${(currentStats.real_return * 100).toFixed(2)}%</p>
                            <p><strong>Volatility:</strong> ${(currentStats.volatility * 100).toFixed(2)}%</p>
                            <p><strong>Real Sharpe Ratio:</strong> ${currentStats.real_sharpe_ratio.toFixed(3)}</p>
                        </div>
                    </div>
                    <p><strong>Risk Level:</strong> ${analysis.risk_level}</p>
                    
                    <h4>Optimal Portfolio (Max Sharpe Ratio):</h4>
                    <p><strong>Expected Return:</strong> ${(data.optimal_portfolio.stats.return * 100).toFixed(2)}%</p>
                    <p><strong>Volatility:</strong> ${(data.optimal_portfolio.stats.volatility * 100).toFixed(2)}%</p>
                    <p><strong>Sharpe Ratio:</strong> ${data.optimal_portfolio.stats.sharpe_ratio.toFixed(3)}</p>
                    
                    <h4>Optimal Allocation:</h4>
                    <ul>
                        ${Object.entries(data.optimal_portfolio.allocation).map(([ticker, weight]) => 
                            `<li><strong>${ticker}:</strong> ${(weight * 100).toFixed(2)}%</li>`
                        ).join('')}
                    </ul>
                    
                    ${data.recommendations.length > 0 ? `
                        <h4>Diversification Recommendations:</h4>
                        <div style="display: grid; gap: 15px; margin-top: 15px;">
                            ${data.recommendations.slice(0, 5).map(rec => {
                                const returnChange = ((rec.new_return - currentStats.return) * 100).toFixed(2);
                                const volatilityChange = ((rec.new_volatility - currentStats.volatility) * 100).toFixed(2);
                                const returnChangeColor = returnChange >= 0 ? '#27ae60' : '#e74c3c';
                                const volatilityChangeColor = volatilityChange <= 0 ? '#27ae60' : '#e74c3c';
                                
                                return `
                                    <div style="border: 1px solid #e1e8ed; border-radius: 8px; padding: 15px; background: #f8f9fa;">
                                        <h5 style="margin: 0 0 10px 0; color: #2c3e50;">
                                            ${rec.ticker} - ${rec.name}
                                        </h5>
                                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 14px;">
                                            <div>
                                                <strong>Nominal Return:</strong> ${(rec.new_return * 100).toFixed(2)}%
                                                <span style="color: ${returnChangeColor};">(${returnChange >= 0 ? '+' : ''}${returnChange}%)</span>
                                            </div>
                                            <div>
                                                <strong>Real Return:</strong> ${((rec.new_return - currentStats.inflation_rate) * 100).toFixed(2)}%
                                            </div>
                                            <div>
                                                <strong>Volatility:</strong> ${(rec.new_volatility * 100).toFixed(2)}%
                                                <span style="color: ${volatilityChangeColor};">(${volatilityChange >= 0 ? '+' : ''}${volatilityChange}%)</span>
                                            </div>
                                            <div>
                                                <strong>Sharpe Ratio:</strong> ${rec.new_return / rec.new_volatility > 0 ? (rec.new_return / rec.new_volatility).toFixed(3) : 'N/A'}
                                                <span style="color: #27ae60;">(+${rec.sharpe_improvement.toFixed(3)})</span>
                                            </div>
                                            <div>
                                                <strong>Correlation:</strong> ${rec.correlation.toFixed(3)}
                                            </div>
                                            <div>
                                                <strong>Inflation Rate:</strong> ${(currentStats.inflation_rate * 100).toFixed(1)}%
                                            </div>
                                        </div>
                                        <div style="margin-top: 10px; font-size: 12px; color: #7f8c8d;">
                                            <strong>Impact:</strong> Adding 10% ${rec.ticker} to your portfolio
                                        </div>
                                    </div>
                                `;
                            }).join('')}
                        </div>
                    ` : ''}
                </div>
                
                <div class="results success">
                    <h3>Efficient Frontier Analysis</h3>
                    <div id="efficientFrontierPlot"></div>
                </div>
            `;
            
            // Show the analysis section
            analysisSection.style.display = 'block';
            
            // Ensure the section is expanded when showing results
            const content = analysisSection.querySelector('.collapsible-content');
            const header = analysisSection.querySelector('.collapsible-header');
            const icon = header.querySelector('.toggle-icon');
            
            content.classList.add('show');
            header.classList.add('active');
            icon.classList.add('rotated');
            
            // Create efficient frontier plot if data is available
            if (data.efficient_frontier_plot) {
                createEfficientFrontierPlot(data.efficient_frontier_plot, currentStats);
            }
        }

        function showOptimizationResults(data) {
            const resultsDiv = document.getElementById('optimizationResults');
            const optimizationSection = document.getElementById('optimizationSection');
            const allocation = data.allocation;
            const stats = data.optimal_stats;
            const alternativeAllocation = data.alternative_allocation;
            const alternativeStats = data.alternative_stats;
            
            let allocationHtml = '<h4>Optimal Allocation (May include 0% allocations):</h4><ul>';
            for (const [ticker, weight] of Object.entries(allocation)) {
                allocationHtml += `<li><strong>${ticker}:</strong> ${(weight * 100).toFixed(2)}%</li>`;
            }
            allocationHtml += '</ul>';
            
            let alternativeAllocationHtml = '<h4>Alternative Allocation (Minimum 1% per asset):</h4><ul>';
            for (const [ticker, weight] of Object.entries(alternativeAllocation)) {
                alternativeAllocationHtml += `<li><strong>${ticker}:</strong> ${(weight * 100).toFixed(2)}%</li>`;
            }
            alternativeAllocationHtml += '</ul>';
            
            let currentStatsHtml = '';
            if (data.current_stats) {
                currentStatsHtml = `
                    <h4>Current Portfolio Performance:</h4>
                    <p><strong>Expected Return:</strong> ${(data.current_stats.return * 100).toFixed(2)}%</p>
                    <p><strong>Volatility:</strong> ${(data.current_stats.volatility * 100).toFixed(2)}%</p>
                    <p><strong>Sharpe Ratio:</strong> ${data.current_stats.sharpe_ratio.toFixed(3)}</p>
                `;
            }
            
            // Calculate performance difference
            const returnDiff = ((alternativeStats.return - stats.return) * 100).toFixed(2);
            const volatilityDiff = ((alternativeStats.volatility - stats.volatility) * 100).toFixed(2);
            const sharpeDiff = (alternativeStats.sharpe_ratio - stats.sharpe_ratio).toFixed(3);
            
            resultsDiv.innerHTML = `
                <div class="results success">
                    <h3>Portfolio Optimization Results</h3>
                    <p><strong>Strategy:</strong> ${data.constraint_used.replace('_', ' ').toUpperCase()}</p>
                    <p><strong>Analysis Period:</strong> ${data.time_period || 2} year${data.time_period > 1 ? 's' : ''} of historical data</p>
                    <p><strong>Minimum Exposure:</strong> ${formatMinExposure(data.min_exposure_used)}</p>
                    ${currentStatsHtml}
                    
                    <div style="display: flex; gap: 20px; margin: 20px 0;">
                        <div style="flex: 1; padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #3498db;">
                            <h4>Optimal Portfolio Performance:</h4>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 10px 0;">
                                <div>
                                    <h5 style="margin: 0 0 5px 0; font-size: 14px; color: #2c3e50;">Nominal</h5>
                                    <p style="margin: 5px 0; font-size: 13px;"><strong>Return:</strong> ${(stats.return * 100).toFixed(2)}%</p>
                                    <p style="margin: 5px 0; font-size: 13px;"><strong>Sharpe:</strong> ${stats.sharpe_ratio.toFixed(3)}</p>
                                </div>
                                <div>
                                    <h5 style="margin: 0 0 5px 0; font-size: 14px; color: #2c3e50;">Real</h5>
                                    <p style="margin: 5px 0; font-size: 13px;"><strong>Return:</strong> ${(stats.real_return * 100).toFixed(2)}%</p>
                                    <p style="margin: 5px 0; font-size: 13px;"><strong>Sharpe:</strong> ${stats.real_sharpe_ratio.toFixed(3)}</p>
                                </div>
                            </div>
                            <p style="margin: 10px 0 0 0;"><strong>Volatility:</strong> ${(stats.volatility * 100).toFixed(2)}%</p>
                            ${allocationHtml}
                        </div>
                        
                        <div style="flex: 1; padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #e74c3c;">
                            <h4>Alternative Portfolio Performance:</h4>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 10px 0;">
                                <div>
                                    <h5 style="margin: 0 0 5px 0; font-size: 14px; color: #2c3e50;">Nominal</h5>
                                    <p style="margin: 5px 0; font-size: 13px;"><strong>Return:</strong> ${(alternativeStats.return * 100).toFixed(2)}% <span style="color: ${returnDiff >= 0 ? '#27ae60' : '#e74c3c'}">(${returnDiff >= 0 ? '+' : ''}${returnDiff}%)</span></p>
                                    <p style="margin: 5px 0; font-size: 13px;"><strong>Sharpe:</strong> ${alternativeStats.sharpe_ratio.toFixed(3)} <span style="color: ${sharpeDiff >= 0 ? '#27ae60' : '#e74c3c'}">(${sharpeDiff >= 0 ? '+' : ''}${sharpeDiff})</span></p>
                                </div>
                                <div>
                                    <h5 style="margin: 0 0 5px 0; font-size: 14px; color: #2c3e50;">Real</h5>
                                    <p style="margin: 5px 0; font-size: 13px;"><strong>Return:</strong> ${(alternativeStats.real_return * 100).toFixed(2)}%</p>
                                    <p style="margin: 5px 0; font-size: 13px;"><strong>Sharpe:</strong> ${alternativeStats.real_sharpe_ratio.toFixed(3)}</p>
                                </div>
                            </div>
                            <p style="margin: 10px 0 0 0;"><strong>Volatility:</strong> ${(alternativeStats.volatility * 100).toFixed(2)}% <span style="color: ${volatilityDiff <= 0 ? '#27ae60' : '#e74c3c'}">(${volatilityDiff >= 0 ? '+' : ''}${volatilityDiff}%)</span></p>
                            ${alternativeAllocationHtml}
                        </div>
                    </div>
                    
                    <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 15px; margin: 20px 0;">
                        <h4>💡 Allocation Comparison</h4>
                        <p><strong>Optimal Allocation:</strong> Maximizes ${data.constraint_used.replace('_', ' ')} but may exclude some assets (0% allocation).</p>
                        <p><strong>Alternative Allocation:</strong> Ensures at least 1% exposure to each asset while staying close to optimal performance.</p>
                        <p><strong>Performance Impact:</strong> The alternative allocation shows the trade-off between diversification and optimal performance.</p>
                    </div>
                </div>
                
                <div class="results success">
                    <h3>Efficient Frontier Analysis</h3>
                    <div id="optimizationFrontierPlot"></div>
                </div>
            `;
            
            // Ensure the section is expanded when showing results
            const content = optimizationSection.querySelector('.collapsible-content');
            const header = optimizationSection.querySelector('.collapsible-header');
            const icon = header.querySelector('.toggle-icon');
            
            content.classList.add('show');
            header.classList.add('active');
            icon.classList.add('rotated');
            
            // Create efficient frontier plot if data is available
            if (data.efficient_frontier_plot) {
                createOptimizationFrontierPlot(data.efficient_frontier_plot, data.current_stats, stats);
            }
        }

        function showSectorResults(data) {
            const resultsDiv = document.getElementById('sectorResults');
            let sectorsHtml = '<h4>Available Sector ETFs:</h4><ul>';
            for (const [sector, etf] of Object.entries(data.sectors)) {
                sectorsHtml += `<li><strong>${sector}:</strong> ${etf}</li>`;
            }
            sectorsHtml += '</ul>';
            
            resultsDiv.innerHTML = `
                <div class="results success">
                    ${sectorsHtml}
                </div>
            `;
        }

        function showError(elementId, message) {
            const element = document.getElementById(elementId);
            element.innerHTML = `<div class="error">${message}</div>`;
            
            // Show the appropriate section when there's an error
            if (elementId === 'analysisResults') {
                document.getElementById('analysisSection').style.display = 'block';
            }
        }

        function showProgress() {
            const progressContainer = document.getElementById('progressContainer');
            const progressFill = document.getElementById('progressFill');
            const progressText = document.getElementById('progressText');
            
            progressContainer.style.display = 'block';
            progressFill.style.width = '0%';
            progressText.textContent = 'Initializing analysis...';
            
            // Simulate progress
            let progress = 0;
            const progressInterval = setInterval(() => {
                progress += Math.random() * 15;
                if (progress > 90) progress = 90;
                
                progressFill.style.width = progress + '%';
                
                if (progress < 30) {
                    progressText.textContent = 'Fetching market data...';
                } else if (progress < 60) {
                    progressText.textContent = 'Calculating portfolio statistics...';
                } else if (progress < 90) {
                    progressText.textContent = 'Generating efficient frontier...';
                }
            }, 200);
            
            // Store interval ID for cleanup
            progressContainer.dataset.intervalId = progressInterval;
        }

        function hideProgress() {
            const progressContainer = document.getElementById('progressContainer');
            const progressFill = document.getElementById('progressFill');
            const progressText = document.getElementById('progressText');
            
            // Complete the progress bar
            progressFill.style.width = '100%';
            progressText.textContent = 'Analysis complete!';
            
            // Clear the interval
            if (progressContainer.dataset.intervalId) {
                clearInterval(parseInt(progressContainer.dataset.intervalId));
            }
            
            // Hide after a short delay
            setTimeout(() => {
                progressContainer.style.display = 'none';
            }, 1000);
        }
        
        function toggleSection(sectionId) {
            const section = document.getElementById(sectionId);
            const header = section.querySelector('.collapsible-header');
            const content = section.querySelector('.collapsible-content');
            const icon = header.querySelector('.toggle-icon');
            
            // Toggle the content
            content.classList.toggle('show');
            
            // Toggle the header active state
            header.classList.toggle('active');
            
            // Rotate the icon
            icon.classList.toggle('rotated');
        }

        function formatMinExposure(minExposure) {
            if (minExposure === null || minExposure === undefined) {
                return '1% (default)';
            } else if (typeof minExposure === 'number') {
                return `${(minExposure * 100).toFixed(1)}% for all securities`;
            } else if (Array.isArray(minExposure)) {
                return minExposure.map(exposure => `${(exposure * 100).toFixed(1)}%`).join(', ') + ' (individual)';
            } else {
                return '1% (default)';
            }
        }

        function createEfficientFrontierPlot(frontierData, currentStats) {
            const ef = frontierData.efficient_frontier;
            const cal = frontierData.capital_allocation_line;
            const tangency = frontierData.tangency_portfolio;
            
            // Prepare data for plotting
            const efVolatility = ef.map(p => p.volatility * 100);
            const efReturns = ef.map(p => p.return * 100);
            const calVolatility = cal.map(p => p.volatility * 100);
            const calReturns = cal.map(p => p.return * 100);
            
            const traces = [
                {
                    x: efVolatility,
                    y: efReturns,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Efficient Frontier',
                    line: { color: '#2E86AB', width: 3 },
                    hovertemplate: 'Volatility: %{x:.2f}%<br>Return: %{y:.2f}%<extra></extra>'
                },
                {
                    x: calVolatility,
                    y: calReturns,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Capital Allocation Line',
                    line: { color: '#A23B72', width: 2, dash: 'dash' },
                    hovertemplate: 'Volatility: %{x:.2f}%<br>Return: %{y:.2f}%<extra></extra>'
                },
                {
                    x: [tangency.volatility * 100],
                    y: [tangency.return * 100],
                    type: 'scatter',
                    mode: 'markers',
                    name: 'Tangency Portfolio',
                    marker: { 
                        color: '#F18F01', 
                        size: 12,
                        symbol: 'star'
                    },
                    hovertemplate: 'Tangency Portfolio<br>Volatility: %{x:.2f}%<br>Return: %{y:.2f}%<extra></extra>'
                },
                {
                    x: [currentStats.volatility * 100],
                    y: [currentStats.return * 100],
                    type: 'scatter',
                    mode: 'markers',
                    name: 'Current Portfolio',
                    marker: { 
                        color: '#C73E1D', 
                        size: 12,
                        symbol: 'circle'
                    },
                    hovertemplate: 'Current Portfolio<br>Volatility: %{x:.2f}%<br>Return: %{y:.2f}%<extra></extra>'
                }
            ];
            
            const layout = {
                title: 'Efficient Frontier with Capital Allocation Line',
                xaxis: {
                    title: 'Portfolio Volatility (%)',
                    gridcolor: '#E5E5E5'
                },
                yaxis: {
                    title: 'Expected Annual Return (%)',
                    gridcolor: '#E5E5E5'
                },
                plot_bgcolor: 'white',
                paper_bgcolor: 'white',
                font: { color: '#2C3E50' },
                legend: {
                    x: 0.02,
                    y: 0.98,
                    bgcolor: 'rgba(255,255,255,0.8)',
                    bordercolor: '#E5E5E5'
                },
                margin: { l: 60, r: 30, t: 60, b: 60 }
            };
            
            Plotly.newPlot('efficientFrontierPlot', traces, layout, {
                responsive: true,
                displayModeBar: true,
                modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
            });
        }

        function createOptimizationFrontierPlot(frontierData, currentStats, optimalStats) {
            const ef = frontierData.efficient_frontier;
            const cal = frontierData.capital_allocation_line;
            const tangency = frontierData.tangency_portfolio;
            
            // Prepare data for plotting
            const efVolatility = ef.map(p => p.volatility * 100);
            const efReturns = ef.map(p => p.return * 100);
            const calVolatility = cal.map(p => p.volatility * 100);
            const calReturns = cal.map(p => p.return * 100);
            
            const traces = [
                {
                    x: efVolatility,
                    y: efReturns,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Efficient Frontier',
                    line: { color: '#2E86AB', width: 3 },
                    hovertemplate: 'Volatility: %{x:.2f}%<br>Return: %{y:.2f}%<extra></extra>'
                },
                {
                    x: calVolatility,
                    y: calReturns,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Capital Allocation Line',
                    line: { color: '#A23B72', width: 2, dash: 'dash' },
                    hovertemplate: 'Volatility: %{x:.2f}%<br>Return: %{y:.2f}%<extra></extra>'
                },
                {
                    x: [tangency.volatility * 100],
                    y: [tangency.return * 100],
                    type: 'scatter',
                    mode: 'markers',
                    name: 'Tangency Portfolio',
                    marker: { 
                        color: '#F18F01', 
                        size: 12,
                        symbol: 'star'
                    },
                    hovertemplate: 'Tangency Portfolio<br>Volatility: %{x:.2f}%<br>Return: %{y:.2f}%<extra></extra>'
                },
                {
                    x: [optimalStats.volatility * 100],
                    y: [optimalStats.return * 100],
                    type: 'scatter',
                    mode: 'markers',
                    name: 'Optimal Portfolio',
                    marker: { 
                        color: '#27AE60', 
                        size: 12,
                        symbol: 'diamond'
                    },
                    hovertemplate: 'Optimal Portfolio<br>Volatility: %{x:.2f}%<br>Return: %{y:.2f}%<extra></extra>'
                }
            ];
            
            // Add current portfolio if available
            if (currentStats) {
                traces.push({
                    x: [currentStats.volatility * 100],
                    y: [currentStats.return * 100],
                    type: 'scatter',
                    mode: 'markers',
                    name: 'Current Portfolio',
                    marker: { 
                        color: '#C73E1D', 
                        size: 12,
                        symbol: 'circle'
                    },
                    hovertemplate: 'Current Portfolio<br>Volatility: %{x:.2f}%<br>Return: %{y:.2f}%<extra></extra>'
                });
            }
            
            const layout = {
                title: 'Efficient Frontier with Capital Allocation Line',
                xaxis: {
                    title: 'Portfolio Volatility (%)',
                    gridcolor: '#E5E5E5'
                },
                yaxis: {
                    title: 'Expected Annual Return (%)',
                    gridcolor: '#E5E5E5'
                },
                plot_bgcolor: 'white',
                paper_bgcolor: 'white',
                font: { color: '#2C3E50' },
                legend: {
                    x: 0.02,
                    y: 0.98,
                    bgcolor: 'rgba(255,255,255,0.8)',
                    bordercolor: '#E5E5E5'
                },
                margin: { l: 60, r: 30, t: 60, b: 60 }
            };
            
            Plotly.newPlot('optimizationFrontierPlot', traces, layout, {
                responsive: true,
                displayModeBar: true,
                modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
            });
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Root route serving the main application interface."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/analyze', methods=['POST'])
def analyze_portfolio_api():
    """Main API endpoint for portfolio analysis."""
    try:
        data = request.json
        tickers = data.get('tickers', [])
        weights = data.get('weights', [])
        time_period = data.get('time_period', 2)  # Default to 2 years
        min_exposure = data.get('min_exposure', None)  # Default to None (will use 1%)
        
        if not tickers or not weights:
            return jsonify({'error': 'Please provide tickers and weights'}), 400
        
        if len(tickers) != len(weights):
            return jsonify({'error': 'Number of tickers must match number of weights'}), 400
        
        # Validate time period
        if time_period < 1 or time_period > 10:
            return jsonify({'error': 'Time period must be between 1 and 10 years'}), 400
        
        # Use the portfolio analysis module with custom time period
        results = analyze_portfolio_with_period(tickers, weights, time_period, min_exposure)
        
        # Add efficient frontier data
        optimizer = PortfolioOptimizer(tickers, time_period=time_period)
        efficient_frontier_data = optimizer.generate_efficient_frontier_with_risk_free(50)
        results['efficient_frontier_plot'] = efficient_frontier_data
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'portfolio-optimizer-api'})

@app.route('/api/sectors', methods=['GET'])
def get_sectors():
    """Get available sector ETFs for recommendations."""
    try:
        sector_etfs = get_sector_etfs()
        return jsonify({'sectors': sector_etfs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/optimize', methods=['POST'])
def optimize_portfolio():
    """Optimize portfolio with custom constraints."""
    try:
        data = request.json
        tickers = data.get('tickers', [])
        constraint = data.get('constraint', 'max_sharpe')  # 'max_sharpe' or 'min_volatility'
        current_weights = data.get('current_weights', None)
        time_period = data.get('time_period', 2)  # Default to 2 years
        min_exposure = data.get('min_exposure', None)  # Default to None (will use 1%)
        
        if not tickers:
            return jsonify({'error': 'Please provide tickers'}), 400
        
        # Validate time period
        if time_period < 1 or time_period > 10:
            return jsonify({'error': 'Time period must be between 1 and 10 years'}), 400
        
        # Initialize optimizer with custom time period
        optimizer = PortfolioOptimizer(tickers, time_period=time_period)
        
        # Find optimal weights
        optimal_weights = optimizer.optimize_portfolio(constraint)
        optimal_stats = optimizer.portfolio_stats(optimal_weights)
        
        # Calculate current portfolio stats if provided
        current_stats = None
        if current_weights:
            current_stats = optimizer.portfolio_stats(np.array(current_weights))
        
        # Generate efficient frontier with risk-free rate
        efficient_frontier_data = optimizer.generate_efficient_frontier_with_risk_free(50)
        
        # Generate alternative allocation with custom minimum exposure
        try:
            if min_exposure is None:
                # Default to 1% for all securities
                alt_optimization = optimizer.optimize_with_minimum_allocation(constraint, 0.01)
            elif isinstance(min_exposure, (int, float)):
                # Single value for all securities
                alt_optimization = optimizer.optimize_with_minimum_allocation(constraint, min_exposure)
            elif isinstance(min_exposure, list) and len(min_exposure) == len(tickers):
                # Individual values for each security
                alt_optimization = optimizer.optimize_with_custom_minimum_allocation(constraint, min_exposure)
            else:
                raise ValueError("Invalid minimum exposure format")
                
            alternative_allocation = {tickers[i]: alt_optimization['weights'][i] for i in range(len(tickers))}
            alternative_stats = alt_optimization['stats']
        except Exception as e:
            # If minimum allocation fails, use equal weights
            equal_weights = np.array([1/len(tickers)] * len(tickers))
            alternative_stats = optimizer.portfolio_stats(equal_weights)
            alternative_allocation = {tickers[i]: equal_weights[i] for i in range(len(tickers))}
        
        response = {
            'optimal_weights': optimal_weights.tolist(),
            'optimal_stats': optimal_stats,
            'allocation': {tickers[i]: optimal_weights[i] for i in range(len(tickers))},
            'alternative_allocation': alternative_allocation,
            'alternative_stats': alternative_stats,
            'efficient_frontier_plot': efficient_frontier_data,
            'constraint_used': constraint,
            'time_period': time_period,
            'min_exposure_used': min_exposure if min_exposure is not None else 0.01
        }
        
        if current_stats:
            response['current_stats'] = current_stats
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/compare', methods=['POST'])
def compare_portfolios():
    """Compare multiple portfolio allocations."""
    try:
        data = request.json
        tickers = data.get('tickers', [])
        portfolios = data.get('portfolios', [])  # List of {name, weights} dicts
        
        if not tickers or not portfolios:
            return jsonify({'error': 'Please provide tickers and portfolios'}), 400
        
        # Initialize optimizer
        optimizer = PortfolioOptimizer(tickers)
        
        comparison_results = []
        
        for portfolio in portfolios:
            name = portfolio.get('name', 'Portfolio')
            weights = np.array(portfolio.get('weights', []))
            
            if len(weights) != len(tickers):
                continue
            
            # Normalize weights
            weights = weights / weights.sum()
            
            # Calculate stats
            stats = optimizer.portfolio_stats(weights)
            
            comparison_results.append({
                'name': name,
                'weights': weights.tolist(),
                'stats': stats,
                'allocation': {tickers[i]: weights[i] for i in range(len(tickers))}
            })
        
        return jsonify({'comparison': comparison_results})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Get diversification recommendations for a portfolio."""
    try:
        data = request.json
        tickers = data.get('tickers', [])
        weights = data.get('weights', [])
        
        if not tickers or not weights:
            return jsonify({'error': 'Please provide tickers and weights'}), 400
        
        if len(tickers) != len(weights):
            return jsonify({'error': 'Number of tickers must match number of weights'}), 400
        
        # Normalize weights
        weights = np.array(weights)
        weights = weights / weights.sum()
        
        # Initialize optimizer
        optimizer = PortfolioOptimizer(tickers)
        
        # Get recommendations using the module function
        from src.analysis.portfolio import analyze_portfolio_gaps
        recommendations = analyze_portfolio_gaps(tickers, weights.tolist(), optimizer)
        
        return jsonify({'recommendations': recommendations})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/blacklitterman', methods=['POST'])
def black_litterman_analysis():
    """Black-Litterman model analysis endpoint."""
    try:
        data = request.json
        tickers = data.get('tickers', [])
        weights = data.get('weights', [])
        time_period = data.get('time_period', 2)
        risk_free_rate = data.get('risk_free_rate', 0.02)
        views = data.get('views', None)
        confidences = data.get('confidences', None)
        
        if not tickers or not weights:
            return jsonify({'error': 'Please provide tickers and weights'}), 400
        
        if len(tickers) != len(weights):
            return jsonify({'error': 'Number of tickers must match number of weights'}), 400
        
        # Validate time period
        if time_period < 1 or time_period > 10:
            return jsonify({'error': 'Time period must be between 1 and 10 years'}), 400
        
        # Use the Black-Litterman analysis function
        results = analyze_portfolio_black_litterman(
            tickers, 
            weights, 
            views=views,
            time_period=time_period,
            risk_free_rate=risk_free_rate
        )
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cache/info', methods=['GET'])
def get_cache_info():
    """Get information about cached data."""
    try:
        data_manager = get_data_manager()
        info = data_manager.get_cache_info()
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear cache files."""
    try:
        data = request.json or {}
        older_than_days = data.get('older_than_days', None)
        
        data_manager = get_data_manager()
        data_manager.clear_cache(older_than_days)
        
        return jsonify({'message': 'Cache cleared successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cache/preload', methods=['POST'])
def preload_cache():
    """Preload cache with common tickers."""
    try:
        data_manager = get_data_manager()
        data_manager.preload_common_tickers()
        
        return jsonify({'message': 'Cache preloaded successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
