"""Endpoint validation logic using getdc and inspectorfhir libraries."""
import re
from typing import Dict, Any


class EndpointValidator:
    """
    Static methods for validating Direct and FHIR endpoints.
    
    Uses getdc for Direct address validation and inspectorfhir for FHIR endpoint validation.
    """
    
    @staticmethod
    def detect_endpoint_type(*, endpoint_text):
        """
        Detect whether endpoint is a Direct address or FHIR URL.
        
        Args:
            endpoint_text: The endpoint string to analyze
            
        Returns:
            str: 'DirectAddress' or 'FHIRAddress'
        """
        # Direct addresses are SMTP-style email addresses
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        # FHIR endpoints are HTTP/HTTPS URLs
        url_pattern = r'^https?://'
        
        if re.match(email_pattern, endpoint_text):
            return 'DirectAddress'
        elif re.match(url_pattern, endpoint_text, re.IGNORECASE):
            return 'FHIRAddress'
        else:
            # Default to FHIRAddress for ambiguous cases
            return 'FHIRAddress'
    
    @staticmethod
    def validate_direct_address(*, address):
        """
        Validate a Direct address using the getdc library.
        
        Args:
            address: The Direct address to validate
            
        Returns:
            dict: Validation results mapped to database schema
        """
        try:
            from getdc import check_direct_address
            
            # Call getdc library to check the Direct address
            result = check_direct_address(address)
            
            # Map getdc results to our database schema
            return EndpointValidator._map_getdc_results(result=result)
            
        except ImportError:
            return {
                'endpoint_type': 'DirectAddress',
                'is_direct_dns': False,
                'is_direct_ldap': False,
                'is_valid_direct': False,
                'is_valid_endpoint': False,
                'validation_error': 'validators.py Error: getdc library not available'
            }
        except Exception as e:
            return {
                'endpoint_type': 'DirectAddress',
                'is_direct_dns': False,
                'is_direct_ldap': False,
                'is_valid_direct': False,
                'is_valid_endpoint': False,
                'validation_error': f'validators.py Error: Direct validation failed - {str(e)}'
            }
    
    @staticmethod
    def validate_fhir_endpoint(*, url):
        """
        Validate a FHIR endpoint using the inspectorfhir library.
        
        Args:
            url: The FHIR endpoint URL to validate
            
        Returns:
            dict: Validation results mapped to database schema
        """
        try:
            from inspectorfhir import InspectorFHIR
            
            # Create inspector instance and check the endpoint
            inspector = InspectorFHIR(url)
            result = inspector.inspect()
            
            # Map inspectorfhir results to our database schema
            return EndpointValidator._map_inspectorfhir_results(result=result, base_url=url)
            
        except ImportError:
            return {
                'endpoint_type': 'FHIRAddress',
                'is_valid_fhir': False,
                'is_valid_endpoint': False,
                'validation_error': 'validators.py Error: inspectorfhir library not available'
            }
        except Exception as e:
            return {
                'endpoint_type': 'FHIRAddress',
                'is_valid_fhir': False,
                'is_valid_endpoint': False,
                'validation_error': f'validators.py Error: FHIR validation failed - {str(e)}'
            }
    
    @staticmethod
    def _map_getdc_results(*, result):
        """
        Map getdc library results to database schema fields.
        
        Args:
            result: Result object from getdc
            
        Returns:
            dict: Mapped validation data
        """
        # Extract relevant fields from getdc result
        # Note: Actual field names may vary based on getdc library implementation
        dns_valid = getattr(result, 'dns_valid', False) if result else False
        ldap_valid = getattr(result, 'ldap_valid', False) if result else False
        
        # Direct address is valid if either DNS or LDAP validation succeeds
        is_valid = dns_valid or ldap_valid
        
        return {
            'endpoint_type': 'DirectAddress',
            'is_direct_dns': dns_valid,
            'is_direct_ldap': ldap_valid,
            'is_valid_direct': is_valid,
            'is_valid_endpoint': is_valid,
            'validation_error': None if is_valid else 'Direct address validation failed'
        }
    
    @staticmethod
    def _map_inspectorfhir_results(*, result, base_url):
        """
        Map inspectorfhir library results to database schema fields.
        
        Args:
            result: Result object from inspectorfhir
            base_url: The base FHIR URL being validated
            
        Returns:
            dict: Mapped validation data
        """
        # Extract and construct various FHIR endpoint URLs
        # Note: Actual field names may vary based on inspectorfhir library implementation
        
        # Construct standard FHIR URLs
        metadata_url = EndpointValidator._construct_url(base_url=base_url, path='metadata')
        
        # Extract discovered URLs from result
        oidc_url = getattr(result, 'oidc_discovery_url', None) if result else None
        smart_1_url = getattr(result, 'smart_discovery_url', None) if result else None
        smart_2_url = getattr(result, 'smart_configuration_url', None) if result else None
        doc_url = getattr(result, 'documentation_url', None) if result else None
        swagger_url = getattr(result, 'swagger_url', None) if result else None
        
        # Check if various resources were found
        metadata_found = getattr(result, 'metadata_found', False) if result else False
        doc_found = getattr(result, 'documentation_found', False) if result else False
        swagger_found = getattr(result, 'swagger_found', False) if result else False
        
        # FHIR endpoint is valid if metadata endpoint responds
        is_valid = metadata_found
        
        return {
            'endpoint_type': 'FHIRAddress',
            'fhir_metadata_url': metadata_url,
            'oidc_discovery_url': oidc_url,
            'smart_discovery_1_url': smart_1_url,
            'smart_discovery_2_url': smart_2_url,
            'documentation_url': doc_url,
            'is_documentation_found': doc_found,
            'swagger_json_url': swagger_url,
            'is_swagger_json_found': swagger_found,
            'is_valid_fhir': is_valid,
            'is_valid_endpoint': is_valid,
            'validation_error': None if is_valid else 'FHIR endpoint validation failed'
        }
    
    @staticmethod
    def _construct_url(*, base_url, path):
        """
        Construct a URL by appending path to base URL.
        
        Args:
            base_url: The base URL
            path: The path to append
            
        Returns:
            str: Constructed URL
        """
        base_url = base_url.rstrip('/')
        return f'{base_url}/{path}'
