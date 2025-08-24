"""
API Routes for Portfolio Optimizer
"""
from flask import jsonify, request
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.analysis.portfolio import PortfolioOptimizer, analyze_portfolio_with_period, get_sector_etfs, BlackLittermanModel, analyze_portfolio_black_litterman, get_data_manager


def register_routes(app):
    """Register all API routes with the Flask app."""
    
    @app.route('/')
    def index():
        """Root route serving the main application interface."""
        from flask import render_template
        return render_template('index.html')
    
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
                    min_exposure_used = 0.01
                elif isinstance(min_exposure, (int, float)):
                    # Single value for all securities
                    alt_optimization = optimizer.optimize_with_minimum_allocation(constraint, min_exposure)
                    min_exposure_used = min_exposure
                elif isinstance(min_exposure, list):
                    # Individual values for each security
                    alt_optimization = optimizer.optimize_with_custom_minimum_allocation(constraint, min_exposure)
                    min_exposure_used = min_exposure
                else:
                    raise ValueError("Invalid minimum exposure format")
                
                alternative_weights = alt_optimization['weights']
                alternative_stats = alt_optimization['stats']
                
            except Exception as e:
                # Fallback to default if optimization fails
                alt_optimization = optimizer.optimize_with_minimum_allocation(constraint, 0.01)
                alternative_weights = alt_optimization['weights']
                alternative_stats = alt_optimization['stats']
                min_exposure_used = 0.01
            
            # Prepare response
            response = {
                'allocation': {tickers[i]: optimal_weights[i] for i in range(len(tickers))},
                'optimal_stats': optimal_stats,
                'alternative_allocation': {tickers[i]: alternative_weights[i] for i in range(len(tickers))},
                'alternative_stats': alternative_stats,
                'current_stats': current_stats,
                'efficient_frontier_plot': efficient_frontier_data,
                'constraint_used': constraint,
                'time_period': time_period,
                'min_exposure_used': min_exposure_used
            }
            
            return jsonify(response)
        
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
