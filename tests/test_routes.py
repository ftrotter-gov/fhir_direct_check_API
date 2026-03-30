"""Integration tests for API routes."""
import pytest
import json
from datetime import datetime, timedelta
from app.models import EndpointValidation
from app import db


class TestHealthEndpoints:
    """Tests for health check endpoints."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_readiness_check(self, client):
        """Test readiness check endpoint."""
        response = client.get('/ready')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ready'


class TestValidateEndpoint:
    """Tests for /validate endpoint."""
    
    def test_validate_requires_endpoints_array(self, client):
        """Test validation requires endpoints array."""
        response = client.post('/validate',
                              json={},
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'endpoints' in data['message']
    
    def test_validate_endpoints_must_be_array(self, client):
        """Test endpoints must be an array."""
        response = client.post('/validate',
                              json={'endpoints': 'not-an-array'},
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'array' in data['message']
    
    def test_validate_requires_at_least_one_endpoint(self, client):
        """Test validation requires at least one endpoint."""
        response = client.post('/validate',
                              json={'endpoints': []},
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'At least one' in data['message']
    
    def test_validate_enforces_max_endpoints(self, client, app):
        """Test validation enforces max endpoints limit."""
        max_endpoints = app.config.get('MAX_ENDPOINTS_PER_REQUEST', 10)
        endpoints = [f'test{i}@example.com' for i in range(max_endpoints + 1)]
        
        response = client.post('/validate',
                              json={'endpoints': endpoints},
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Maximum' in data['message']
    
    def test_validate_single_endpoint(self, client):
        """Test validating a single endpoint."""
        response = client.post('/validate',
                              json={'endpoints': ['test@example.com']},
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'results' in data
        assert 'test@example.com' in data['results']
        assert data['total_endpoints'] == 1
    
    def test_validate_multiple_endpoints(self, client):
        """Test validating multiple endpoints."""
        endpoints = ['test1@example.com', 'https://fhir.example.com']
        response = client.post('/validate',
                              json={'endpoints': endpoints},
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['results']) == 2
        assert data['total_endpoints'] == 2
    
    def test_validate_uses_cache(self, client, app, sample_cached_record):
        """Test validation uses cached results."""
        with app.app_context():
            endpoint_text = sample_cached_record.endpoint_text
        
        response = client.post('/validate',
                              json={'endpoints': [endpoint_text]},
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['results'][endpoint_text]['from_cache'] is True
    
    def test_validate_response_includes_from_cache_flag(self, client):
        """Test validation response includes from_cache flag."""
        response = client.post('/validate',
                              json={'endpoints': ['new@example.com']},
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'from_cache' in data['results']['new@example.com']


class TestDownloadEndpoint:
    """Tests for /download endpoint."""
    
    def test_download_empty_database(self, client):
        """Test download with empty database."""
        response = client.get('/download')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total'] == 0
        assert data['data'] == []
    
    def test_download_with_data(self, client, app, sample_cached_record):
        """Test download with data in database."""
        response = client.get('/download')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total'] >= 1
        assert len(data['data']) >= 1
    
    def test_download_default_pagination(self, client):
        """Test download uses default pagination."""
        response = client.get('/download')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['page'] == 1
        assert data['per_page'] == 100
    
    def test_download_custom_pagination(self, client):
        """Test download with custom pagination."""
        response = client.get('/download?page=2&per_page=50')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['page'] == 2
        assert data['per_page'] == 50
    
    def test_download_pagination_info(self, client):
        """Test download includes pagination info."""
        response = client.get('/download')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_pages' in data
        assert 'has_next' in data
        assert 'has_prev' in data
    
    def test_download_max_per_page_limit(self, client):
        """Test download enforces max per_page limit."""
        response = client.get('/download?per_page=2000')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['per_page'] <= 1000


class TestModelMethods:
    """Tests for database model methods."""
    
    def test_is_cache_valid_recent(self, app, sample_cached_record):
        """Test cache validity for recent record."""
        with app.app_context():
            record = EndpointValidation.query.first()
            assert record.is_cache_valid(validity_months=6) is True
    
    def test_is_cache_valid_old(self, app):
        """Test cache validity for old record."""
        with app.app_context():
            old_record = EndpointValidation(
                endpoint_type='DirectAddress',
                endpoint_text='old@example.com',
                last_checked=datetime.utcnow() - timedelta(days=200),
                is_valid_endpoint=True
            )
            db.session.add(old_record)
            db.session.commit()
            
            assert old_record.is_cache_valid(validity_months=6) is False
    
    def test_to_dict_conversion(self, app, sample_cached_record):
        """Test model to_dict conversion."""
        with app.app_context():
            record = EndpointValidation.query.first()
            result = record.to_dict()
            
            assert isinstance(result, dict)
            assert 'endpoint_type' in result
            assert 'endpoint_text' in result
            assert 'is_valid_endpoint' in result
    
    def test_upsert_creates_new(self, app):
        """Test upsert creates new record."""
        with app.app_context():
            data = {
                'endpoint_type': 'DirectAddress',
                'is_valid_endpoint': True
            }
            record = EndpointValidation.upsert(
                endpoint_text='new@example.com',
                validation_data=data
            )
            assert record.endpoint_text == 'new@example.com'
            assert record.is_valid_endpoint is True
    
    def test_upsert_updates_existing(self, app, sample_cached_record):
        """Test upsert updates existing record."""
        with app.app_context():
            original_text = sample_cached_record.endpoint_text
            
            data = {
                'endpoint_type': 'DirectAddress',
                'is_valid_endpoint': False
            }
            record = EndpointValidation.upsert(
                endpoint_text=original_text,
                validation_data=data
            )
            
            assert record.endpoint_text == original_text
            assert record.is_valid_endpoint is False
