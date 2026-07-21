#!/usr/bin/env python3
"""
Test script to verify PTaaSRetestCompletion schema validation
"""
from src.api.v1.schemas.ptaas_retest import PTaaSRetestCompletion, RetestResult
from pydantic import ValidationError
import json

def test_valid_payload():
    """Test with valid payload"""
    print("✅ Testing valid payload...")
    
    # Test 1: With evidence
    data1 = {
        "retest_result": "FIXED",
        "retest_notes": "The vulnerability has been completely fixed. I tested multiple scenarios and confirmed the fix works.",
        "retest_evidence": ["https://example.com/screenshot1.png"]
    }
    
    try:
        completion = PTaaSRetestCompletion(**data1)
        print(f"   ✓ Valid with evidence: {completion.model_dump()}")
    except ValidationError as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test 2: Without evidence (None)
    data2 = {
        "retest_result": "NOT_FIXED",
        "retest_notes": "The vulnerability still exists. The fix was not properly implemented.",
        "retest_evidence": None
    }
    
    try:
        completion = PTaaSRetestCompletion(**data2)
        print(f"   ✓ Valid without evidence (None): {completion.model_dump()}")
    except ValidationError as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test 3: Without evidence field at all
    data3 = {
        "retest_result": "PARTIALLY_FIXED",
        "retest_notes": "Some aspects were fixed but issues remain in the authentication flow."
    }
    
    try:
        completion = PTaaSRetestCompletion(**data3)
        print(f"   ✓ Valid without evidence field: {completion.model_dump()}")
    except ValidationError as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test 4: With empty list
    data4 = {
        "retest_result": "NEW_ISSUE",
        "retest_notes": "The fix introduced a new security vulnerability in the session management.",
        "retest_evidence": []
    }
    
    try:
        completion = PTaaSRetestCompletion(**data4)
        print(f"   ✓ Valid with empty list: {completion.model_dump()}")
    except ValidationError as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    return True

def test_invalid_payload():
    """Test with invalid payloads"""
    print("\n❌ Testing invalid payloads (should fail)...")
    
    # Test 1: Invalid result value
    data1 = {
        "retest_result": "INVALID_STATUS",
        "retest_notes": "This should fail because the status is invalid"
    }
    
    try:
        completion = PTaaSRetestCompletion(**data1)
        print(f"   ✗ Should have failed but didn't: {completion.model_dump()}")
        return False
    except ValidationError as e:
        print(f"   ✓ Correctly rejected invalid result: {e.errors()[0]['msg']}")
    
    # Test 2: Notes too short
    data2 = {
        "retest_result": "FIXED",
        "retest_notes": "Too short"
    }
    
    try:
        completion = PTaaSRetestCompletion(**data2)
        print(f"   ✗ Should have failed but didn't: {completion.model_dump()}")
        return False
    except ValidationError as e:
        print(f"   ✓ Correctly rejected short notes: {e.errors()[0]['msg']}")
    
    # Test 3: Missing required fields
    data3 = {
        "retest_result": "FIXED"
    }
    
    try:
        completion = PTaaSRetestCompletion(**data3)
        print(f"   ✗ Should have failed but didn't: {completion.model_dump()}")
        return False
    except ValidationError as e:
        print(f"   ✓ Correctly rejected missing notes: {e.errors()[0]['msg']}")
    
    return True

def test_enum_values():
    """Test enum values"""
    print("\n🔍 Testing enum values...")
    
    for result in RetestResult:
        print(f"   • {result.name} = {result.value}")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("PTaaS Retest Completion Schema Validation Test")
    print("=" * 60)
    
    success = True
    success = test_valid_payload() and success
    success = test_invalid_payload() and success
    success = test_enum_values() and success
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    print("=" * 60)
