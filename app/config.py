"""Configuration management for FHIR Direct Check API."""
import os


class Config:
    """Base configuration class with default settings."""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://fhir_user:fhir_password@localhost:5432/fhir_direct_check'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API settings
    MAX_ENDPOINTS_PER_REQUEST = int(os.getenv('MAX_ENDPOINTS_PER_REQUEST', '10'))
    CACHE_VALIDITY_MONTHS = int(os.getenv('CACHE_VALIDITY_MONTHS', '6'))
    RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', '100'))
    RATE_LIMIT_PERIOD_MINUTES = int(os.getenv('RATE_LIMIT_PERIOD_MINUTES', '5'))


class DevelopmentConfig(Config):
    """Development environment configuration."""
    
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production environment configuration."""
    
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing environment configuration."""
    
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URL',
        'postgresql://fhir_user:fhir_password@localhost:5432/fhir_direct_check_test'
    )


# Configuration dictionary
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
