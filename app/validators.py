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
            import sys
            # Import workaround: getdc has broken relative imports
            from gdc import parse_certificate
            sys.modules['parse_certificate'] = parse_certificate
            from gdc import get_direct_certificate
            
            # Call getdc library to check the Direct address
            dcert = get_direct_certificate.DCert(address)
            result = dcert.validate_certificate(download_certificate=False)
            
            # Map getdc results to our database schema
            return EndpointValidator._map_getdc_results(result=result)
            
        except ImportError as e:
            return {
                'endpoint_type': 'DirectAddress',
                'is_direct_dns': False,
                'is_direct_ldap': False,
                'is_valid_direct': False,
                'is_valid_endpoint': False,
                'validation_error': f'validators.py Error: getdc library not available - {str(e)}'
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
            from inspectorfhir import ifhir
            
            # Use fhir_recognizer to check the FHIR endpoint
            # Note: build_result_report() has a bug, use fhir_recognizer() instead
            result = ifhir.fhir_recognizer(url)
            
            # Map inspectorfhir results to our database schema
            return EndpointValidator._map_inspectorfhir_results(result=result, base_url=url)
            
        except ImportError as e:
            return {
                'endpoint_type': 'FHIRAddress',
                'is_valid_fhir': False,
                'is_valid_endpoint': False,
                'validation_error': f'validators.py Error: inspectorfhir library not available - {str(e)}'
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
            result: Result dict from dcert.validate_certificate()
                    Structure: {
                        'is_found': bool,
                        'dns': {'is_found': bool, 'status': int, 'message': str, ...},
                        'ldap': {'is_found': bool, 'status': int, 'message': str, ...}
                    }
            
        Returns:
            dict: Mapped validation data
        """
        if not result or not isinstance(result, dict):
            return {
                'endpoint_type': 'DirectAddress',
                'is_direct_dns': False,
                'is_direct_ldap': False,
                'is_valid_direct': False,
                'is_valid_endpoint': False,
                'validation_error': 'validators.py Error: Invalid result from getdc'
            }
        
        # Extract DNS and LDAP validation results
        dns_result = result.get('dns', {})
        ldap_result = result.get('ldap', {})
        
        dns_valid = dns_result.get('is_found', False) if isinstance(dns_result, dict) else False
        ldap_valid = ldap_result.get('is_found', False) if isinstance(ldap_result, dict) else False
        
        # Overall validation - either DNS or LDAP must succeed
        is_valid = result.get('is_found', False)
        
        # Build error message if validation failed
        error_msg = None
        if not is_valid:
            dns_msg = dns_result.get('message', 'Unknown DNS error') if isinstance(dns_result, dict) else 'DNS check failed'
            ldap_msg = ldap_result.get('message', 'Unknown LDAP error') if isinstance(ldap_result, dict) else 'LDAP check failed'
            error_msg = f'DNS: {dns_msg}; LDAP: {ldap_msg}'
        
        return {
            'endpoint_type': 'DirectAddress',
            'is_direct_dns': dns_valid,
            'is_direct_ldap': ldap_valid,
            'is_valid_direct': is_valid,
            'is_valid_endpoint': is_valid,
            'validation_error': error_msg
        }
    
    @staticmethod
    def _map_inspectorfhir_results(*, result, base_url):
        """
        Map inspectorfhir library results to database schema fields.
        
        Args:
            result: Result dict from ifhir.fhir_recognizer()
                    Structure: {
                        'report': {
                            'fhir_metadata': {'url': str, 'found': bool},
                            'oidc_discovery': {'url': str, 'found': bool},
                            'smart_discovery_1': {'url': str, 'found': bool},
                            'smart_discovery_2': {'url': str, 'found': bool},
                            'documentation_ui': {'found': bool, <urls>: bool},
                            'swagger_json': {'found': bool, <urls>: bool}
                        },
                        'details': {...}  # Full error details
                    }
            base_url: The base FHIR URL being validated
            
        Returns:
            dict: Mapped validation data
        """
        if not result or not isinstance(result, dict):
            return {
                'endpoint_type': 'FHIRAddress',
                'is_valid_fhir': False,
                'is_valid_endpoint': False,
                'validation_error': 'validators.py Error: Invalid result from inspectorfhir'
            }
        
        # Get the report section which has simplified results
        report = result.get('report', {})
        if not isinstance(report, dict):
            report = {}
        
        # Extract FHIR metadata check
        fhir_metadata = report.get('fhir_metadata', {})
        metadata_found = fhir_metadata.get('found', False) if isinstance(fhir_metadata, dict) else False
        metadata_url = fhir_metadata.get('url') if isinstance(fhir_metadata, dict) else None
        
        # Extract OIDC discovery
        oidc_discovery = report.get('oidc_discovery', {})
        oidc_url = oidc_discovery.get('url') if isinstance(oidc_discovery, dict) else None
        
        # Extract SMART discovery URLs
        smart_1 = report.get('smart_discovery_1', {})
        smart_1_url = smart_1.get('url') if isinstance(smart_1, dict) else None
        
        smart_2 = report.get('smart_discovery_2', {})
        smart_2_url = smart_2.get('url') if isinstance(smart_2, dict) else None
        
        # Extract documentation UI info
        doc_ui = report.get('documentation_ui', {})
        doc_found = doc_ui.get('found', False) if isinstance(doc_ui, dict) else False
        # Find first documentation URL that was found
        doc_url = None
        if isinstance(doc_ui, dict):
            for key, value in doc_ui.items():
                if key != 'found' and value is True:
                    doc_url = key
                    break
        
        # Extract Swagger/OpenAPI info
        swagger_json = report.get('swagger_json', {})
        swagger_found = swagger_json.get('found', False) if isinstance(swagger_json, dict) else False
        # Find first swagger URL that was found
        swagger_url = None
        if isinstance(swagger_json, dict):
            for key, value in swagger_json.items():
                if key != 'found' and value is True:
                    swagger_url = key
                    break
        
        # FHIR endpoint is valid if metadata endpoint responds
        is_valid = metadata_found
        
        # Build error message if validation failed
        error_msg = None
        if not is_valid:
            details = result.get('details', {})
            if isinstance(details, dict) and 'fhir_metadata' in details:
                fhir_meta_details = details['fhir_metadata']
                if isinstance(fhir_meta_details, dict):
                    error_msg = fhir_meta_details.get('error', 'FHIR metadata endpoint not found')
        
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
            'validation_error': error_msg
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
