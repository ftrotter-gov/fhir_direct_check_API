#!/usr/bin/env python3
"""
Test to understand the actual APIs of both libraries.
"""

print("=" * 60)
print("Understanding Library APIs")
print("=" * 60)

# Test 1: getdc - Call the validation methods
print("\n1. Testing getdc DCert methods...")
test_address = "22688EL@mchd.cernerdirect.com"
print(f"   Address: {test_address}")

try:
    import sys
    from gdc import parse_certificate
    sys.modules['parse_certificate'] = parse_certificate
    from gdc import get_direct_certificate
    
    dcert = get_direct_certificate.DCert(test_address)
    print(f"   ✓ DCert object created")
    print(f"   Methods: {[m for m in dir(dcert) if not m.startswith('_') and callable(getattr(dcert, m))]}")
    
    # Try calling get_certificate to perform validation
    print(f"\n   Calling dcert.get_certificate()...")
    dcert.get_certificate()
    
    print(f"   After get_certificate():")
    print(f"   - result: {dcert.result}")
    print(f"   - dns_response: {dcert.dns_response}")
    print(f"   - ldap_response: {dcert.ldap_response}")
        
except Exception as e:
    print(f"   ✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 2: inspectorfhir - Use individual functions
print("\n2. Testing inspectorfhir individual functions...")
test_url = "https://epicfhir.aurora.org/FHIR/MYAURORA/api/FHIR/DSTU2/"
print(f"   URL: {test_url}")

try:
    from inspectorfhir import ifhir
    
    # Try check_fhir_metadata directly
    print(f"\n   Calling ifhir.check_fhir_metadata()...")
    metadata_result = ifhir.check_fhir_metadata(test_url)
    print(f"   Metadata result: {metadata_result}")
    
    # Try fhir_recognizer to identify the URL structure
    print(f"\n   Calling ifhir.fhir_recognizer()...")
    recognizer_result = ifhir.fhir_recognizer(test_url)
    print(f"   Recognizer result type: {type(recognizer_result)}")
    if isinstance(recognizer_result, dict):
        print(f"   Recognizer keys: {recognizer_result.keys()}")
        for key, value in list(recognizer_result.items())[:10]:  # Show first 10 items
            print(f"   - {key}: {value}")
    
    # Try check_smart_discovery
    print(f"\n   Calling ifhir.check_smart_discovery()...")
    smart_result = ifhir.check_smart_discovery(test_url)
    print(f"   SMART discovery result: {smart_result}")
    
except Exception as e:
    print(f"   ✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("API Understanding Complete")
print("=" * 60)
