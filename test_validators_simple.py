#!/usr/bin/env python3
"""
Simple test to verify validators work with actual library calls.
"""
import json

print("=" * 80)
print("SIMPLE VALIDATOR TEST")
print("=" * 80)

# Test 1: Direct Address Validation
print("\n1. Testing Direct Address Validator...")
print("-" * 80)

from app.validators import EndpointValidator

test_direct = "22688EL@mchd.cernerdirect.com"
print(f"Address: {test_direct}")
print("Calling EndpointValidator.validate_direct_address()...")

try:
    result = EndpointValidator.validate_direct_address(address=test_direct)
    print("\n✓ Validation completed")
    print("\nResult:")
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Endpoint Type Detection
print("\n" + "=" * 80)
print("2. Testing Endpoint Type Detection...")
print("-" * 80)

test_cases = [
    "test@example.com",
    "https://example.com/fhir",
    "http://localhost:8080/api",
    "not-an-endpoint"
]

for endpoint in test_cases:
    endpoint_type = EndpointValidator.detect_endpoint_type(endpoint_text=endpoint)
    print(f"  {endpoint:40} -> {endpoint_type}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
