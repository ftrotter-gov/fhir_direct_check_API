"""Flask application factory for FHIR Direct Check API."""
import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()


def create_app():
    """
    Create and configure the Flask application.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'postgresql://fhir_user:fhir_password@localhost:5432/fhir_direct_check'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # API configuration
    app.config['MAX_ENDPOINTS_PER_REQUEST'] = int(os.getenv('MAX_ENDPOINTS_PER_REQUEST', '10'))
    app.config['CACHE_VALIDITY_MONTHS'] = int(os.getenv('CACHE_VALIDITY_MONTHS', '6'))
    app.config['RATE_LIMIT_REQUESTS'] = int(os.getenv('RATE_LIMIT_REQUESTS', '100'))
    app.config['RATE_LIMIT_PERIOD_MINUTES'] = int(os.getenv('RATE_LIMIT_PERIOD_MINUTES', '5'))
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    from app.routes import api_blueprint
    app.register_blueprint(api_blueprint)
    
    return app


def register_error_handlers(app):
    """
    Register error handlers for common HTTP errors.
    
    Args:
        app: Flask application instance
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': str(error)
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({
            'error': 'Rate Limit Exceeded',
            'message': 'You have exceeded the rate limit of 100 requests per 5 minutes'
        }), 429
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500
