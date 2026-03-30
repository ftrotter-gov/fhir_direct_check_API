"""Unit tests for validator module."""
import pytest
from app.validators import EndpointValidator


class TestEndpointTypeDetection:
    """Tests for endpoint type detection."""
    
    def test_detect_direct_address(self):
        """Test detection of Direct address."""
        result = EndpointValidator.detect_endpoint_type(
            endpoint_text='test@example.com'
        )
        assert result == 'DirectAddress'
    
    def test_detect_fhir_url_https(self):
        """Test detection of FHIR HTTPS URL."""
        result = EndpointValidator.detect_endpoint_type(
            endpoint_text='https://fhir.example.com/api'
        )
        assert result == 'FHIRAddress'
    
    def test_detect_fhir_url_http(self):
        """Test detection of FHIR HTTP URL."""
        result = EndpointValidator.detect_endpoint_type(
            endpoint_text='http://fhir.example.com/api'
        )
        assert result == 'FHIRAddress'
    
    def test_detect_ambiguous_defaults_to_fhir(self):
        """Test ambiguous input defaults to FHIR."""
        result = EndpointValidator.detect_endpoint_type(
            endpoint_text='not-a-valid-endpoint'
        )
        assert result == 'FHIRAddress'


class TestDirectAddressValidation:
    """Tests for Direct address validation."""
    
    def test_validate_direct_returns_dict(self):
        """Test Direct validation returns dictionary."""
        result = EndpointValidator.validate_direct_address(
            address='test@example.com'
        )
        assert isinstance(result, dict)
        assert 'endpoint_type' in result
        assert result['endpoint_type'] == 'DirectAddress'
    
    def test_validate_direct_has_required_fields(self):
        """Test Direct validation result has required fields."""
        result = EndpointValidator.validate_direct_address(
            address='test@example.com'
        )
        assert 'is_direct_dns' in result
        assert 'is_direct_ldap' in result
        assert 'is_valid_direct' in result
        assert 'is_valid_endpoint' in result


class TestFHIREndpointValidation:
    """Tests for FHIR endpoint validation."""
    
    def test_validate_fhir_returns_dict(self):
        """Test FHIR validation returns dictionary."""
        result = EndpointValidator.validate_fhir_endpoint(
            url='https://fhir.example.com'
        )
        assert isinstance(result, dict)
        assert 'endpoint_type' in result
        assert result['endpoint_type'] == 'FHIRAddress'
    
    def test_validate_fhir_has_required_fields(self):
        """Test FHIR validation result has required fields."""
        result = EndpointValidator.validate_fhir_endpoint(
            url='https://fhir.example.com'
        )
        # Always has these fields
        assert 'endpoint_type' in result
        assert 'is_valid_fhir' in result
        assert 'is_valid_endpoint' in result
        # May have fhir_metadata_url if library is available
        # If library not available, will have validation_error
        assert 'fhir_metadata_url' in result or 'validation_error' in result


class TestURLConstruction:
    """Tests for URL construction helper."""
    
    def test_construct_url_basic(self):
        """Test basic URL construction."""
        result = EndpointValidator._construct_url(
            base_url='https://example.com',
            path='metadata'
        )
        assert result == 'https://example.com/metadata'
    
    def test_construct_url_removes_trailing_slash(self):
        """Test URL construction with trailing slash."""
        result = EndpointValidator._construct_url(
            base_url='https://example.com/',
            path='metadata'
        )
        assert result == 'https://example.com/metadata'
