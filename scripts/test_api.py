#!/usr/bin/env python3
"""
Test script for the portfolio optimizer API
"""

import requests
import json

def test_api():
    """Test the portfolio optimizer API endpoints."""
    
    base_url = "http://localhost:5000"
    
    # Test health endpoint
    print("Testing health endpoint...")
    response = requests.get(f"{base_url}/api/health")
    print(f"Health Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # Test portfolio analysis
    print("Testing portfolio analysis...")
    data = {
        "tickers": ["AAPL", "MSFT"],
        "weights": [0.6, 0.4]
    }
    
    response = requests.post(f"{base_url}/api/analyze", json=data)
    print(f"Analysis Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("Analysis successful!")
        print(f"Current Sharpe Ratio: {result['current_portfolio']['stats']['sharpe_ratio']:.3f}")
        print(f"Optimal Sharpe Ratio: {result['optimal_portfolio']['stats']['sharpe_ratio']:.3f}")
        print(f"Recommendations: {len(result['recommendations'])} found")
    else:
        print(f"Error: {response.text}")
    
    print()
    
    # Test sectors endpoint
    print("Testing sectors endpoint...")
    response = requests.get(f"{base_url}/api/sectors")
    print(f"Sectors Status: {response.status_code}")
    if response.status_code == 200:
        sectors = response.json()
        print(f"Available sectors: {len(sectors['sectors'])}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_api()
