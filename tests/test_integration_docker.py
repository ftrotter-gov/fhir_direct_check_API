"""
Integration tests that run against a live Docker instance.

These tests spin up the API using docker-compose and test against real endpoints
from the test_data directory.
"""
import pytest
import requests
import subprocess
import time
import os
from pathlib import Path


# Test data file paths
TEST_DATA_DIR = Path(__file__).parent.parent / 'test_data'
GOOD_DIRECT_FILE = TEST_DATA_DIR / 'good_direct_addresses.txt'
BAD_DIRECT_FILE = TEST_DATA_DIR / 'bad_direct_addresses.txt'
GOOD_FHIR_FILE = TEST_DATA_DIR / 'good_fhir_urls.txt'
BAD_FHIR_FILE = TEST_DATA_DIR / 'bad_fhir_urls.txt'


def read_test_endpoints(*, filepath):
    """
    Read endpoints from test data file.
    
    Args:
        filepath: Path to test data file
        
    Returns:
        list: List of endpoint strings (comments and empty lines filtered)
    """
    if not filepath.exists():
        return []
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Filter out comments and empty lines
    endpoints = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            endpoints.append(line)
    
    return endpoints


@pytest.fixture(scope='module')
def docker_api():
    """
    Fixture to manage Docker Compose lifecycle for integration tests.
    
    Starts docker-compose before tests and tears it down after.
    """
    # Get the project directory
    project_dir = Path(__file__).parent.parent
    
    # Start docker-compose
    print("\n🚀 Starting Docker Compose services...")
    subprocess.run(
        ['docker-compose', 'up', '-d', '--build'],
        cwd=project_dir,
        check=True,
        capture_output=True
    )
    
    # Wait for services to be healthy
    api_url = 'http://localhost:5000'
    max_retries = 30
    retry_delay = 2
    
    print(f"⏳ Waiting for API to be ready at {api_url}...")
    for i in range(max_retries):
        try:
            response = requests.get(f'{api_url}/health', timeout=5)
            if response.status_code == 200:
                print(f"✅ API is ready after {i * retry_delay} seconds")
                break
        except requests.exceptions.RequestException:
            if i < max_retries - 1:
                time.sleep(retry_delay)
            else:
                # Cleanup on failure
                subprocess.run(['docker-compose', 'down'], cwd=project_dir)
                raise Exception(f"API failed to start after {max_retries * retry_delay} seconds")
    
    # Yield to run tests
    yield api_url
    
    # Teardown - stop docker-compose
    print("\n🛑 Stopping Docker Compose services...")
    subprocess.run(['docker-compose', 'down'], cwd=project_dir, check=True)


class TestDockerIntegration:
    """Integration tests against live Docker service."""
    
    def test_health_endpoint(self, docker_api):
        """Test health endpoint is accessible."""
        response = requests.get(f'{docker_api}/health')
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
    
    def test_ready_endpoint(self, docker_api):
        """Test readiness endpoint is accessible."""
        response = requests.get(f'{docker_api}/ready')
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'ready'
    
    def test_good_direct_addresses(self, docker_api):
        """
        Test validation of good Direct addresses from test data.
        
        Note: This may fail if the addresses are not actually valid Direct addresses.
        The test is primarily checking that the API processes them without errors.
        """
        endpoints = read_test_endpoints(filepath=GOOD_DIRECT_FILE)
        
        if not endpoints:
            pytest.skip("No good Direct addresses in test data file")
        
        response = requests.post(
            f'{docker_api}/validate',
            json={'endpoints': endpoints},
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'results' in data
        assert len(data['results']) == len(endpoints)
        
        # Check each endpoint was processed
        for endpoint in endpoints:
            assert endpoint in data['results']
            result = data['results'][endpoint]
            assert 'endpoint_type' in result
            assert result['endpoint_type'] == 'DirectAddress'
            # Note: Not asserting is_valid_direct=True because addresses may not be valid
            print(f"\n  {endpoint}: valid={result.get('is_valid_direct', False)}")
    
    def test_bad_direct_addresses(self, docker_api):
        """
        Test validation of bad Direct addresses from test data.
        
        These should return is_valid_direct: false
        """
        endpoints = read_test_endpoints(filepath=BAD_DIRECT_FILE)
        
        if not endpoints:
            pytest.skip("No bad Direct addresses in test data file")
        
        response = requests.post(
            f'{docker_api}/validate',
            json={'endpoints': endpoints},
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'results' in data
        assert len(data['results']) == len(endpoints)
        
        # Check each endpoint was processed
        for endpoint in endpoints:
            assert endpoint in data['results']
            result = data['results'][endpoint]
            assert 'endpoint_type' in result
            assert result['endpoint_type'] == 'DirectAddress'
            assert result.get('is_valid_direct', True) is False
            print(f"\n  {endpoint}: valid={result.get('is_valid_direct', None)}")
    
    def test_good_fhir_urls(self, docker_api):
        """
        Test validation of good FHIR URLs from test data.
        
        Note: This may fail if the URLs are not actually valid FHIR endpoints.
        The test is primarily checking that the API processes them without errors.
        """
        endpoints = read_test_endpoints(filepath=GOOD_FHIR_FILE)
        
        if not endpoints:
            pytest.skip("No good FHIR URLs in test data file")
        
        response = requests.post(
            f'{docker_api}/validate',
            json={'endpoints': endpoints},
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'results' in data
        assert len(data['results']) == len(endpoints)
        
        # Check each endpoint was processed
        for endpoint in endpoints:
            assert endpoint in data['results']
            result = data['results'][endpoint]
            assert 'endpoint_type' in result
            assert result['endpoint_type'] == 'FHIRAddress'
            # Note: Not asserting is_valid_fhir=True because URLs may not be valid
            print(f"\n  {endpoint}: valid={result.get('is_valid_fhir', False)}")
    
    def test_bad_fhir_urls(self, docker_api):
        """
        Test validation of bad FHIR URLs from test data.
        
        These should return is_valid_fhir: false
        """
        endpoints = read_test_endpoints(filepath=BAD_FHIR_FILE)
        
        if not endpoints:
            pytest.skip("No bad FHIR URLs in test data file")
        
        response = requests.post(
            f'{docker_api}/validate',
            json={'endpoints': endpoints},
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'results' in data
        assert len(data['results']) == len(endpoints)
        
        # Check each endpoint was processed
        for endpoint in endpoints:
            assert endpoint in data['results']
            result = data['results'][endpoint]
            assert 'endpoint_type' in result
            assert result['endpoint_type'] == 'FHIRAddress'
            assert result.get('is_valid_fhir', True) is False
            print(f"\n  {endpoint}: valid={result.get('is_valid_fhir', None)}")
    
    def test_caching_behavior(self, docker_api):
        """Test that caching works correctly."""
        test_endpoint = ['test.cache@example.com']
        
        # First request - fresh validation
        response1 = requests.post(
            f'{docker_api}/validate',
            json={'endpoints': test_endpoint},
            headers={'Content-Type': 'application/json'}
        )
        
        assert response1.status_code == 200
        data1 = response1.json()
        result1 = data1['results'][test_endpoint[0]]
        assert result1['from_cache'] is False
        
        # Second request - should use cache
        response2 = requests.post(
            f'{docker_api}/validate',
            json={'endpoints': test_endpoint},
            headers={'Content-Type': 'application/json'}
        )
        
        assert response2.status_code == 200
        data2 = response2.json()
        result2 = data2['results'][test_endpoint[0]]
        assert result2['from_cache'] is True
    
    def test_download_endpoint(self, docker_api):
        """Test download endpoint returns paginated data."""
        response = requests.get(f'{docker_api}/download?per_page=10')
        
        assert response.status_code == 200
        data = response.json()
        assert 'data' in data
        assert 'page' in data
        assert 'total' in data
        assert data['page'] == 1
        assert data['per_page'] == 10
    
    def test_mixed_endpoints(self, docker_api):
        """Test validation of mixed Direct and FHIR endpoints."""
        # Get one of each type if available
        direct_endpoints = read_test_endpoints(filepath=BAD_DIRECT_FILE)
        fhir_endpoints = read_test_endpoints(filepath=BAD_FHIR_FILE)
        
        mixed = []
        if direct_endpoints:
            mixed.append(direct_endpoints[0])
        if fhir_endpoints:
            mixed.append(fhir_endpoints[0])
        
        if not mixed:
            pytest.skip("No test data available for mixed endpoint test")
        
        response = requests.post(
            f'{docker_api}/validate',
            json={'endpoints': mixed},
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data['results']) == len(mixed)


class TestDockerRateLimiting:
    """Test rate limiting behavior."""
    
    def test_rate_limiting_enforced(self, docker_api):
        """
        Test that rate limiting is enforced for non-localhost.
        
        Note: This test may not work as expected if running from localhost,
        as localhost is exempt from rate limiting.
        """
        # Make multiple requests to test rate limiting
        # Since we're likely running from localhost, this will succeed
        # but we can still verify the rate limit headers
        
        response = requests.post(
            f'{docker_api}/validate',
            json={'endpoints': ['ratelimit@test.com']},
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 200
        
        # Check for rate limit headers (may be absent for localhost)
        if 'X-RateLimit-Limit' in response.headers:
            assert int(response.headers['X-RateLimit-Limit']) > 0
            print(f"\nRate limit: {response.headers['X-RateLimit-Limit']}")
        else:
            print("\nNo rate limit headers (likely running from localhost)")
