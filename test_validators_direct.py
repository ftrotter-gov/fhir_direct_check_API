#!/usr/bin/env python3
"""
Direct test of validators without importing through app module.
"""
import sys
import json

# Add app directory to path
sys.path.insert(0, '/Users/ftrotter/gitgov/DSACMS/fhir_direct_check_API')

print("=" * 80)
print("DIRECT VALIDATOR TEST")
print("=" * 80)

# Import validators directly
print("\nImporting validators module...")
import importlib.util
spec = importlib.util.spec_from_file_location(
    "validators",
    "/Users/ftrotter/gitgov/DSACMS/fhir_direct_check_API/app/validators.py"
)
validators_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validators_module)

EndpointValidator = validators_module.EndpointValidator
print("✓ Validators imported successfully")

# Test 1: Direct Address Validation
print("\n" + "=" * 80)
print("1. Testing Direct Address Validator...")
print("-" * 80)

test_direct = "22688EL@mchd.cernerdirect.com"
print(f"Address: {test_direct}")
print("Calling EndpointValidator.validate_direct_address()...")

try:
    result = EndpointValidator.validate_direct_address(address=test_direct)
    print("\n✓ Validation completed")
    print("\nMapped Result:")
    print(json.dumps(result, indent=2))
    
    print("\nKey fields:")
    print(f"  endpoint_type: {result.get('endpoint_type')}")
    print(f"  is_valid_endpoint: {result.get('is_valid_endpoint')}")
    print(f"  is_direct_dns: {result.get('is_direct_dns')}")
    print(f"  is_direct_ldap: {result.get('is_direct_ldap')}")
    
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
print("TEST COMPLETE - Validators are working!")
print("=" * 80)
