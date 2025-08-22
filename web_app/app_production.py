"""
Portfolio Optimizer Web Application - Production Version
Optimized for deployment on Render.com
"""

import os
import sys
from flask import Flask
from flask_cors import CORS

# Add the web_app directory to the Python path
sys.path.append(os.path.dirname(__file__))
from routes import register_routes

def create_app():
    """Create and configure the Flask application for production."""
    app = Flask(__name__)
    
    # Enable CORS for production
    CORS(app)
    
    # Register all routes
    register_routes(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get('PORT', 5000))
    
    # Use 0.0.0.0 to bind to all available network interfaces
    app.run(host='0.0.0.0', port=port, debug=False)
