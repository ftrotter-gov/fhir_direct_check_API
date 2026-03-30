"""Pytest fixtures for testing."""
import pytest
from app import create_app, db
from app.models import EndpointValidation


@pytest.fixture
def app():
    """Create and configure test app."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def sample_direct_address():
    """Sample Direct address for testing."""
    return 'test@direct.example.com'


@pytest.fixture
def sample_fhir_url():
    """Sample FHIR URL for testing."""
    return 'https://fhir.example.com/api'


@pytest.fixture
def sample_cached_record(app, sample_direct_address):
    """Create a sample cached record."""
    with app.app_context():
        record = EndpointValidation(
            endpoint_type='DirectAddress',
            endpoint_text=sample_direct_address,
            is_direct_dns=True,
            is_direct_ldap=False,
            is_valid_direct=True,
            is_valid_endpoint=True
        )
        db.session.add(record)
        db.session.commit()
        return record
