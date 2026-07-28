"""
TEST SCRIPT - Simple version without emoji for Windows console
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from tools import (
    get_personality_profile,
    calculate_compatibility,
    search_matches,
    get_relationship_advice
)

print("="*60)
print("CUPID AGENT - TEST SUITE")
print("="*60)

# Test 1: get_personality_profile
print("\n[TEST 1] get_personality_profile")
print("-"*60)
print("\n1.1 Valid user 'minh':")
result = get_personality_profile("minh")
print(result)
print("PASS" if "Minh" in result else "FAIL")

print("\n1.2 Invalid user 'xyz123':")
result = get_personality_profile("xyz123")
print(result)
print("PASS" if "LOI" in result or "LỖI" in result else "FAIL")

# Test 2: calculate_compatibility
print("\n[TEST 2] calculate_compatibility")
print("-"*60)
print("\n2.1 Minh and Linh:")
result = calculate_compatibility("minh", "linh")
print(result)
print("PASS" if "Minh" in result and "Linh" in result else "FAIL")

print("\n2.2 Invalid user1:")
result = calculate_compatibility("xyz", "linh")
print(result)
print("PASS" if "LOI" in result or "LỖI" in result else "FAIL")

# Test 3: search_matches
print("\n[TEST 3] search_matches")
print("-"*60)
print("\n3.1 Find matches for 'minh' (min=40):")
result = search_matches("minh", min_compatibility=40)
print(result)
print("PASS")

print("\n3.2 Invalid user:")
result = search_matches("xyz123")
print(result)
print("PASS" if "LOI" in result or "LỖI" in result else "FAIL")

# Test 4: get_relationship_advice
print("\n[TEST 4] get_relationship_advice")
print("-"*60)
print("\n4.1 First date advice:")
result = get_relationship_advice("hen ho dau tien")
print(result)
print("PASS" if "1." in result else "FAIL")

print("\n4.2 General advice:")
result = get_relationship_advice("other situation")
print(result)
print("PASS" if "1." in result else "FAIL")

print("\n" + "="*60)
print("ALL TESTS COMPLETED!")
print("="*60)
