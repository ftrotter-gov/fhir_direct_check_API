#!/usr/bin/env python3
"""
Test script to verify the two core libraries (getdc/gdc and inspectorfhir) are working.
"""

print("=" * 60)
print("Testing Core Libraries")
print("=" * 60)

# Test 1: Import gdc
print("\n1. Testing gdc (getdc) library import...")
try:
    import gdc
    print("   ✓ gdc package imports successfully")
except Exception as e:
    print(f"   ✗ ERROR importing gdc: {e}")

# Test 2: Import inspectorfhir
print("\n2. Testing inspectorfhir library import...")
try:
    import inspectorfhir
    print("   ✓ inspectorfhir package imports successfully")
except Exception as e:
    print(f"   ✗ ERROR importing inspectorfhir: {e}")

# Test 3: Try importing inspectorfhir.ifhir
print("\n3. Testing inspectorfhir.ifhir module...")
try:
    from inspectorfhir import ifhir
    print("   ✓ inspectorfhir.ifhir imports successfully")
    print(f"   Available functions: {[x for x in dir(ifhir) if not x.startswith('_')]}")
except Exception as e:
    print(f"   ✗ ERROR importing inspectorfhir.ifhir: {e}")

# Test 4: Try importing gdc modules directly
print("\n4. Testing gdc.get_direct_certificate module...")
try:
    from gdc import get_direct_certificate
    print("   ✓ gdc.get_direct_certificate imports successfully")
except Exception as e:
    print(f"   ✗ ERROR importing gdc.get_direct_certificate: {e}")

# Test 5: Try importing gdc.parse_certificate
print("\n5. Testing gdc.parse_certificate module...")
try:
    from gdc import parse_certificate
    print("   ✓ gdc.parse_certificate imports successfully")
except Exception as e:
    print(f"   ✗ ERROR importing gdc.parse_certificate: {e}")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)
