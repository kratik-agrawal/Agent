from flask import Flask
from flask_cors import CORS
from .config import Config, validate_config
from .routes.company_routes import company_bp
from .routes.prompt_routes import prompt_bp

def create_app():
    """Application factory function"""
    # Validate configuration
    try:
        validate_config()
    except ValueError as e:
        print(f"Configuration error: {e}")
        raise
    
    # Create Flask app
    app = Flask(__name__)
    
    # Configure app
    app.config.from_object(Config)
    
    # Initialize CORS
    CORS(app, origins=Config.CORS_ORIGINS)
    
    # Register blueprints
    app.register_blueprint(company_bp)
    app.register_blueprint(prompt_bp)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy', 'timestamp': '2025-01-27T00:00:00Z'}
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(
        debug=Config.DEBUG,
        port=Config.PORT,
        host='0.0.0.0'
    ) 