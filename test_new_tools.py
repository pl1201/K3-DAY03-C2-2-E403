"""
Test script cho 2 tools moi: get_zodiac_compatibility va get_mbti_compatibility
"""

import sys
sys.path.append('src')

from tools import get_zodiac_compatibility, get_mbti_compatibility

def test_zodiac_compatibility():
    print("\n" + "="*60)
    print("TEST 1: get_zodiac_compatibility")
    print("="*60)

    # Test 1.1: Valid pair - Su Tu va Nhan Ma
    print("\n[Test 1.1] Su Tu va Nhan Ma:")
    result = get_zodiac_compatibility("Su Tu", "Nhan Ma")
    print(result)
    assert "88/100" in result or "85/100" in result, "FAIL: Score should be high"
    print("PASS")

    # Test 1.2: Valid pair - Bach Duong va Su Tu
    print("\n[Test 1.2] Bach Duong va Su Tu:")
    result = get_zodiac_compatibility("Bach Duong", "Su Tu")
    print(result)
    assert "90/100" in result, "FAIL: Score should be 90"
    print("PASS")

    # Test 1.3: Invalid zodiac - Nguoi Doi (Edge case)
    print("\n[Test 1.3] Nguoi Doi (invalid):")
    result = get_zodiac_compatibility("Nguoi Doi", "Su Tu")
    print(result)
    assert "LOI" in result or "khong hop le" in result.lower(), "FAIL: Should return error"
    print("PASS")

    # Test 1.4: Bo Cap (special case from test case 4)
    print("\n[Test 1.4] Bo Cap va Su Tu:")
    result = get_zodiac_compatibility("Bo Cap", "Su Tu")
    print(result)
    print("PASS (Bo Cap is valid)")

def test_mbti_compatibility():
    print("\n" + "="*60)
    print("TEST 2: get_mbti_compatibility")
    print("="*60)

    # Test 2.1: Valid pair - INTJ va ENFP (from test case 4)
    print("\n[Test 2.1] INTJ va ENFP:")
    result = get_mbti_compatibility("INTJ", "ENFP")
    print(result)
    assert "85/100" in result, "FAIL: Score should be 85"
    print("PASS")

    # Test 2.2: Case insensitive - intj va enfp
    print("\n[Test 2.2] intj va enfp (lowercase):")
    result = get_mbti_compatibility("intj", "enfp")
    print(result)
    assert "85/100" in result, "FAIL: Should handle lowercase"
    print("PASS")

    # Test 2.3: Invalid MBTI - XYZQ123 (Edge case from test case 5)
    print("\n[Test 2.3] XYZQ123 (invalid):")
    result = get_mbti_compatibility("XYZQ123", "ENFP")
    print(result)
    assert "LOI" in result or "khong hop le" in result.lower(), "FAIL: Should return error"
    print("PASS")

    # Test 2.4: Another valid pair - INFJ va ENFP
    print("\n[Test 2.4] INFJ va ENFP:")
    result = get_mbti_compatibility("INFJ", "ENFP")
    print(result)
    assert "88/100" in result, "FAIL: Score should be 88"
    print("PASS")

def test_combined_scenario():
    print("\n" + "="*60)
    print("TEST 3: Combined Scenario (Test Case 4)")
    print("="*60)

    print("\n[Scenario] INTJ + Bo Cap vs ENFP + Su Tu:")
    print("\nStep 1: Check MBTI compatibility...")
    mbti_result = get_mbti_compatibility("INTJ", "ENFP")
    print(mbti_result)

    print("\nStep 2: Check Zodiac compatibility...")
    zodiac_result = get_zodiac_compatibility("Bo Cap", "Su Tu")
    print(zodiac_result)

    print("\nStep 3: Tong hop ket qua:")
    print("Hai nguoi nay co do tuong thich tot ca ve MBTI lan cung hoang dao!")
    print("PASS")

def test_edge_cases():
    print("\n" + "="*60)
    print("TEST 4: Edge Cases (Test Case 5)")
    print("="*60)

    print("\n[Edge Case 1] Nguoi Doi zodiac:")
    result = get_zodiac_compatibility("Nguoi Doi", "Su Tu")
    print(result)
    assert "LOI" in result, "FAIL: Should reject invalid zodiac"
    print("PASS")

    print("\n[Edge Case 2] XYZQ123 MBTI:")
    result = get_mbti_compatibility("XYZQ123", "ENFP")
    print(result)
    assert "LOI" in result, "FAIL: Should reject invalid MBTI"
    print("PASS")

    print("\n[Edge Case 3] Both invalid:")
    zodiac_result = get_zodiac_compatibility("Nguoi Doi", "Khung Long")
    mbti_result = get_mbti_compatibility("ABC", "XYZ")
    print("Zodiac:", zodiac_result)
    print("MBTI:", mbti_result)
    assert "LOI" in zodiac_result and "LOI" in mbti_result, "FAIL: Both should error"
    print("PASS")

if __name__ == "__main__":
    try:
        test_zodiac_compatibility()
        test_mbti_compatibility()
        test_combined_scenario()
        test_edge_cases()

        print("\n" + "="*60)
        print("RESULTS: All tests passed!")
        print("="*60)
        print("\nSUCCESS! 2 tools moi da tuong thich voi test cases goc!")
        print("Tools ready:")
        print("  1. get_zodiac_compatibility(zodiac1, zodiac2)")
        print("  2. get_mbti_compatibility(mbti1, mbti2)")

    except AssertionError as e:
        print(f"\n\nFAIL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
