"""
Portfolio Optimizer Web Application
A modular Flask application for portfolio analysis and optimization.
"""

from flask import Flask
from flask_cors import CORS
from routes import register_routes

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Enable CORS for development
    CORS(app)
    
    # Register all routes
    register_routes(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("🚀 Starting Portfolio Optimizer...")
    print("📊 Application available at: http://127.0.0.1:5000")
    print("🔧 API endpoints:")
    print("   - GET  /api/health     - Health check")
    print("   - POST /api/analyze    - Portfolio analysis")
    print("   - POST /api/optimize   - Portfolio optimization")
    print("   - GET  /api/sectors    - Sector recommendations")
    print("=" * 50)
    
    app.run(debug=True, host='127.0.0.1', port=5000)
