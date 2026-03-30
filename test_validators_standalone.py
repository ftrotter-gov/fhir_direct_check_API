#!/usr/bin/env python3
"""
Test the validator functions directly without importing Flask app.
"""
import re

print("=" * 60)
print("Testing Validators Standalone")
print("=" * 60)

# Test 1: Direct Address Validation with getdc
print("\n1. Testing Direct Address Validation with getdc...")
test_address = "22688EL@mchd.cernerdirect.com"
print(f"   Address: {test_address}")

try:
    import sys
    from gdc import parse_certificate
    sys.modules['parse_certificate'] = parse_certificate
    from gdc import get_direct_certificate
    
    dcert = get_direct_certificate.DCert(test_address)
    print(f"   ✓ DCert object created")
    print(f"   Attributes: {[attr for attr in dir(dcert) if not attr.startswith('_') and not callable(getattr(dcert, attr))]}")
    
    # Show actual values
    print(f"\n   Checking actual DCert properties:")
    print(f"   - endpoint: {dcert.endpoint}")
    print(f"   - result: {dcert.result}")
    
    # Try to call the methods to get DNS/LDAP info
    if hasattr(dcert, 'dns_response'):
        print(f"   - dns_response: {dcert.dns_response}")
    if hasattr(dcert, 'ldap_response'):
        print(f"   - ldap_response: {dcert.ldap_response}")
        
except Exception as e:
    print(f"   ✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 2: FHIR Endpoint Validation with inspectorfhir
print("\n2. Testing FHIR Endpoint Validation with inspectorfhir...")
test_url = "https://epicfhir.aurora.org/FHIR/MYAURORA/api/FHIR/DSTU2/"
print(f"   URL: {test_url}")

try:
    from inspectorfhir import ifhir
    
    result = ifhir.build_result_report(test_url)
    print(f"   ✓ build_result_report() completed")
    print(f"   Result type: {type(result)}")
    
    if isinstance(result, dict):
        print(f"   Result keys: {result.keys()}")
        for key, value in result.items():
            if isinstance(value, str) and len(str(value)) > 100:
                print(f"   - {key}: {str(value)[:100]}...")
            else:
                print(f"   - {key}: {value}")
    else:
        print(f"   Result: {result}")
        
except Exception as e:
    print(f"   ✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)
