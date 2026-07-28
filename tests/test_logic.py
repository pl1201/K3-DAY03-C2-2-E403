"""
TEST SCRIPT - Logic only (no printing emoji output)
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from tools import (
    get_personality_profile,
    calculate_compatibility,
    search_matches,
    get_relationship_advice
)

print("="*60)
print("CUPID AGENT - TEST SUITE (Logic Check)")
print("="*60)

# Test 1: get_personality_profile
print("\n[TEST 1] get_personality_profile")
print("-"*60)

result = get_personality_profile("tien")
test1_1 = "Tien" in result and "25" in result
print(f"1.1 Valid user 'tien': {'PASS' if test1_1 else 'FAIL'}")

result = get_personality_profile("xyz123")
test1_2 = "LOI" in result or "LỖI" in result
print(f"1.2 Invalid user: {'PASS' if test1_2 else 'FAIL'}")

result = get_personality_profile("TIEN")
test1_3 = "Tien" in result
print(f"1.3 Case insensitive: {'PASS' if test1_3 else 'FAIL'}")

# Test 2: calculate_compatibility
print("\n[TEST 2] calculate_compatibility")
print("-"*60)

result = calculate_compatibility("tien", "lan")
test2_1 = "Tien" in result and "Lan" in result and "/100" in result
print(f"2.1 Valid pair: {'PASS' if test2_1 else 'FAIL'}")

result = calculate_compatibility("xyz", "lan")
test2_2 = "LOI" in result or "LỖI" in result
print(f"2.2 Invalid user1: {'PASS' if test2_2 else 'FAIL'}")

result = calculate_compatibility("tien", "abc")
test2_3 = "LOI" in result or "LỖI" in result
print(f"2.3 Invalid user2: {'PASS' if test2_3 else 'FAIL'}")

# Test 3: search_matches
print("\n[TEST 3] search_matches")
print("-"*60)

result = search_matches("tien", min_compatibility=40)
test3_1 = "Tim" in result or "Tìm" in result or "Khong" in result or "Không" in result
print(f"3.1 Search with low threshold: {'PASS' if test3_1 else 'FAIL'}")

result = search_matches("xyz123")
test3_2 = "LOI" in result or "LỖI" in result
print(f"3.2 Invalid user: {'PASS' if test3_2 else 'FAIL'}")

result = search_matches("tien", min_compatibility=100)
test3_3 = "Khong" in result or "Không" in result
print(f"3.3 High threshold (no results): {'PASS' if test3_3 else 'FAIL'}")

# Test 4: get_relationship_advice
print("\n[TEST 4] get_relationship_advice")
print("-"*60)

result = get_relationship_advice("hen ho dau tien")
test4_1 = "1." in result and "2." in result
print(f"4.1 First date advice: {'PASS' if test4_1 else 'FAIL'}")

result = get_relationship_advice("giu lua")
test4_2 = "1." in result and "2." in result
print(f"4.2 Keep love advice: {'PASS' if test4_2 else 'FAIL'}")

result = get_relationship_advice("other")
test4_3 = "1." in result and "2." in result
print(f"4.3 General advice: {'PASS' if test4_3 else 'FAIL'}")

# Summary
print("\n" + "="*60)
all_tests = [
    test1_1, test1_2, test1_3,
    test2_1, test2_2, test2_3,
    test3_1, test3_2, test3_3,
    test4_1, test4_2, test4_3
]
passed = sum(all_tests)
total = len(all_tests)
print(f"RESULTS: {passed}/{total} tests passed")
print("="*60)

if passed == total:
    print("\nSUCCESS! All tools are working correctly!")
    print("Ready for integration into ReAct Agent.")
else:
    print(f"\nWARNING: {total - passed} test(s) failed.")
    print("Please check the tools implementation.")
