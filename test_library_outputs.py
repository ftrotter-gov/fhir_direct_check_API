#!/usr/bin/env python3
"""
Comprehensive test to understand actual library output structures.
"""
import json
import sys

print("=" * 80)
print("COMPREHENSIVE LIBRARY OUTPUT TEST")
print("=" * 80)

# Test 1: getdc library with validate_certificate
print("\n" + "=" * 80)
print("1. GETDC LIBRARY - validate_certificate() OUTPUT")
print("=" * 80)

try:
    from gdc import parse_certificate
    sys.modules['parse_certificate'] = parse_certificate
    from gdc import get_direct_certificate
    
    test_address = "22688EL@mchd.cernerdirect.com"
    print(f"\nTesting: {test_address}")
    
    dcert = get_direct_certificate.DCert(test_address)
    result = dcert.validate_certificate(download_certificate=False)
    
    print("\n✓ validate_certificate() completed successfully")
    print("\nFull result structure:")
    print(json.dumps(result, indent=2, default=str))
    
    print("\nKey fields to extract:")
    print(f"  - is_found: {result.get('is_found')}")
    if 'dns' in result:
        print(f"  - dns.is_found: {result['dns'].get('is_found')}")
        print(f"  - dns.status: {result['dns'].get('status')}")
    if 'ldap' in result:
        print(f"  - ldap.is_found: {result['ldap'].get('is_found')}")
        print(f"  - ldap.status: {result['ldap'].get('status')}")
        
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 2: inspectorfhir library with fhir_recognizer
print("\n" + "=" * 80)
print("2. INSPECTORFHIR LIBRARY - fhir_recognizer() OUTPUT")
print("=" * 80)

try:
    from inspectorfhir import ifhir
    
    test_url = "https://epicfhir.aurora.org/FHIR/MYAURORA/api/FHIR/DSTU2/"
    print(f"\nTesting: {test_url}")
    
    result = ifhir.fhir_recognizer(test_url)
    
    print("\n✓ fhir_recognizer() completed successfully")
    print("\nFull result structure (truncated for readability):")
    
    if isinstance(result, dict):
        print(f"\nTop-level keys: {list(result.keys())}")
        
        if 'report' in result:
            print(f"\nreport keys: {list(result['report'].keys())}")
            print("\nreport content:")
            print(json.dumps(result['report'], indent=2, default=str))
        
        if 'details' in result:
            print(f"\ndetails keys: {list(result['details'].keys())}")
            # Show summary of details without full errors
            for key, value in result['details'].items():
                if isinstance(value, dict):
                    if 'found' in value:
                        print(f"  - {key}: found={value['found']}, url={value.get('url', 'N/A')}")
                    else:
                        print(f"  - {key}: {list(value.keys())}")
                        
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 3: inspectorfhir with individual check functions
print("\n" + "=" * 80)
print("3. INSPECTORFHIR LIBRARY - Individual check_* functions")
print("=" * 80)

try:
    from inspectorfhir import ifhir
    
    test_url = "https://epicfhir.aurora.org/FHIR/MYAURORA/api/FHIR/DSTU2/"
    
    print(f"\n3a. check_fhir_metadata('{test_url}'):")
    metadata_result = ifhir.check_fhir_metadata(test_url)
    print(json.dumps(metadata_result, indent=2, default=str))
    
    print(f"\n3b. check_smart_discovery('{test_url}'):")
    smart_result = ifhir.check_smart_discovery(test_url)
    print(json.dumps(smart_result, indent=2, default=str))
    
    print(f"\n3c. check_oidc_discovery('{test_url}'):")
    oidc_result = ifhir.check_oidc_discovery(test_url)
    print(json.dumps(oidc_result, indent=2, default=str))
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
