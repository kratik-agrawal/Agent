#!/usr/bin/env python3
"""
Simple script to run the Flask application with proper environment setup.
"""
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Flask environment variables
os.environ['FLASK_APP'] = 'app.py'
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

if __name__ == '__main__':
    from app import app
    app.run(
        debug=True,
        port=5001,
        host='0.0.0.0'
    ) 