#!/usr/bin/env python3
"""
Test the validators.py module with correct library usage.
"""
import sys
sys.path.insert(0, '/Users/ftrotter/gitgov/DSACMS/fhir_direct_check_API')

from app.validators import EndpointValidator

print("=" * 60)
print("Testing EndpointValidator")
print("=" * 60)

# Test 1: Direct Address Validation
print("\n1. Testing Direct Address Validation...")
test_address = "22688EL@mchd.cernerdirect.com"
print(f"   Address: {test_address}")

try:
    result = EndpointValidator.validate_direct_address(address=test_address)
    print(f"   ✓ Validation completed")
    print(f"   Result: {result}")
except Exception as e:
    print(f"   ✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 2: FHIR Endpoint Validation
print("\n2. Testing FHIR Endpoint Validation...")
test_url = "https://epicfhir.aurora.org/FHIR/MYAURORA/api/FHIR/DSTU2/"
print(f"   URL: {test_url}")

try:
    result = EndpointValidator.validate_fhir_endpoint(url=test_url)
    print(f"   ✓ Validation completed")
    print(f"   Result: {result}")
except Exception as e:
    print(f"   ✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Endpoint Type Detection
print("\n3. Testing Endpoint Type Detection...")
test_cases = [
    "22688EL@mchd.cernerdirect.com",
    "https://epicfhir.aurora.org/FHIR/MYAURORA/api/FHIR/DSTU2/",
    "test@example.com",
    "http://fhir.example.com"
]

for endpoint in test_cases:
    detected_type = EndpointValidator.detect_endpoint_type(endpoint_text=endpoint)
    print(f"   {endpoint[:50]:50} -> {detected_type}")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)
