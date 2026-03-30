#!/usr/bin/env python3
"""
Test script to validate actual Direct addresses and FHIR URLs using the core libraries.
"""

print("=" * 60)
print("Testing Actual Validation with Core Libraries")
print("=" * 60)

# Test inspectorfhir with a FHIR URL
print("\n1. Testing inspectorfhir with a FHIR URL...")
try:
    from inspectorfhir import ifhir
    
    # Test with Epic's FHIR endpoint from test data
    test_url = "https://epicfhir.aurora.org/FHIR/MYAURORA/api/FHIR/DSTU2/"
    print(f"   Testing URL: {test_url}")
    
    result = ifhir.check_fhir_metadata(test_url)
    print(f"   ✓ inspectorfhir.ifhir.check_fhir_metadata() executed")
    print(f"   Result: {result}")
    
except Exception as e:
    print(f"   ✗ ERROR testing inspectorfhir: {e}")
    import traceback
    traceback.print_exc()

# Test getdc with a Direct address
print("\n2. Testing getdc with a Direct address...")
try:
    # Import parse_certificate which works
    from gdc import parse_certificate
    print("   ✓ gdc.parse_certificate imports successfully")
    
    # Try to work around the broken import in get_direct_certificate
    print("   Attempting to fix the import issue in gdc.get_direct_certificate...")
    import sys
    from gdc import parse_certificate
    # Add parse_certificate to sys.modules so the broken import can find it
    sys.modules['parse_certificate'] = parse_certificate
    
    # Now try importing get_direct_certificate
    from gdc import get_direct_certificate
    print("   ✓ gdc.get_direct_certificate imports successfully (with workaround)")
    
    # Test with a Direct address from test data
    test_address = "22688EL@mchd.cernerdirect.com"
    print(f"   Testing Direct address: {test_address}")
    
    dcert = get_direct_certificate.DCert(test_address)
    print(f"   ✓ Created DCert object")
    print(f"   Result: {dcert}")
    
except Exception as e:
    print(f"   ✗ ERROR testing getdc: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)
