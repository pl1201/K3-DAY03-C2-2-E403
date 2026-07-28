"""
TEST SCRIPT - KIEM TRA CAC TOOLS DOC LAP
Chay script nay de test tung tool mot cach rieng biet truoc khi tich hop vao Agent.
"""

import sys
import os

# Dam bao import tu src/ hoat dong
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from tools import (
    get_personality_profile,
    calculate_compatibility,
    search_matches,
    get_relationship_advice,
    USER_DATABASE
)

def print_header(title):
    """In header dep cho moi test"""
    print("\n" + "="*60)
    print(f"TEST: {title}")
    print("="*60)

def test_get_personality_profile():
    """Test tool lay ho so nguoi dung"""
    print_header("TEST 1: get_personality_profile")

    # Test case 1: User hop le
    print("\n[OK] Test 1.1: User hop le - 'minh'")
    result = get_personality_profile("minh")
    print(result)
    assert "Minh" in result, "Phai chua ten Minh"
    assert "25" in result, "Phai chua tuoi 25"
    print("[PASS]")

    # Test case 2: User khong ton tai
    print("\n[ERROR] Test 1.2: User khong ton tai - 'xyz123'")
    result = get_personality_profile("xyz123")
    print(result)
    assert "LỖI" in result or "LOI" in result, "Phai tra ve thong bao loi"
    assert "xyz123" in result, "Phai chua ten user bi loi"
    print("[PASS] - Xu ly loi dung")

    # Test case 3: Case insensitive
    print("\n[OK] Test 1.3: Case insensitive - 'MINH'")
    result = get_personality_profile("MINH")
    print(result)
    assert "Minh" in result, "Phai hoat dong voi uppercase"
    print("[PASS]")

def test_calculate_compatibility():
    """Test tool tính độ tương thích"""
    print_header("TEST 2: calculate_compatibility")

    # Test case 1: Cặp có độ tương thích cao
    print("\n💕 Test 2.1: Minh và Linh (có sở thích chung)")
    result = calculate_compatibility("minh", "linh")
    print(result)
    assert "Minh" in result and "Linh" in result
    assert "/100" in result, "Phải có điểm tổng hợp"
    print("✅ PASS")

    # Test case 2: User1 không tồn tại
    print("\n❌ Test 2.2: User1 không tồn tại")
    result = calculate_compatibility("xyz", "linh")
    print(result)
    assert "LỖI" in result, "Phải trả về lỗi"
    print("✅ PASS - Xử lý lỗi đúng")

    # Test case 3: User2 không tồn tại
    print("\n❌ Test 2.3: User2 không tồn tại")
    result = calculate_compatibility("minh", "abc")
    print(result)
    assert "LỖI" in result, "Phải trả về lỗi"
    print("✅ PASS - Xử lý lỗi đúng")

    # Test case 4: Kiểm tra thuật toán
    print("\n🧮 Test 2.4: Kiểm tra logic tính điểm")
    result = calculate_compatibility("huy", "nga")
    print(result)
    assert "30/100" in result or "Điểm sở thích" in result
    print("✅ PASS - Thuật toán đúng")

def test_search_matches():
    """Test tool tìm kiếm đối tượng phù hợp"""
    print_header("TEST 3: search_matches")

    # Test case 1: Tìm với threshold mặc định
    print("\n🔍 Test 3.1: Tìm đối tượng cho Minh (min=60)")
    result = search_matches("minh", min_compatibility=60)
    print(result)
    assert "Tìm thấy" in result or "Không tìm thấy" in result
    print("✅ PASS")

    # Test case 2: Tìm với threshold thấp
    print("\n🔍 Test 3.2: Tìm với threshold thấp (min=40)")
    result = search_matches("minh", min_compatibility=40)
    print(result)
    print("✅ PASS")

    # Test case 3: User không tồn tại
    print("\n❌ Test 3.3: User không tồn tại")
    result = search_matches("xyz123")
    print(result)
    assert "LỖI" in result, "Phải trả về lỗi"
    print("✅ PASS - Xử lý lỗi đúng")

    # Test case 4: Threshold cao (100) - không ai đạt
    print("\n🔍 Test 3.4: Threshold quá cao (min=100)")
    result = search_matches("minh", min_compatibility=100)
    print(result)
    assert "Không tìm thấy" in result
    print("✅ PASS")

def test_get_relationship_advice():
    """Test tool lời khuyên mối quan hệ"""
    print_header("TEST 4: get_relationship_advice")

    # Test case 1: Hẹn hò đầu tiên
    print("\n💝 Test 4.1: Lời khuyên hẹn hò đầu tiên")
    result = get_relationship_advice("hẹn hò đầu tiên")
    print(result)
    assert "hẹn" in result.lower()
    assert "1." in result and "2." in result, "Phải có danh sách lời khuyên"
    print("✅ PASS")

    # Test case 2: Giữ lửa
    print("\n🔥 Test 4.2: Lời khuyên giữ lửa")
    result = get_relationship_advice("giữ lửa tình yêu")
    print(result)
    assert "1." in result and "2." in result
    print("✅ PASS")

    # Test case 3: Xung đột
    print("\n⚖️ Test 4.3: Lời khuyên giải quyết xung đột")
    result = get_relationship_advice("xung đột trong tình yêu")
    print(result)
    assert "1." in result and "2." in result
    print("✅ PASS")

    # Test case 4: Tình huống không có trong database
    print("\n💡 Test 4.4: Tình huống chung")
    result = get_relationship_advice("tình huống khác")
    print(result)
    assert "1." in result, "Phải trả về lời khuyên chung"
    print("✅ PASS - Fallback đúng")

def test_database_integrity():
    """Kiểm tra tính toàn vẹn của database"""
    print_header("TEST 5: Database Integrity")

    print("\n📊 Kiểm tra USER_DATABASE:")
    print(f"   Số lượng users: {len(USER_DATABASE)}")

    required_fields = ["name", "age", "gender", "personality",
                      "interests", "zodiac", "relationship_status", "looking_for"]

    for user_id, profile in USER_DATABASE.items():
        print(f"\n   ✓ User '{user_id}':")
        for field in required_fields:
            assert field in profile, f"User {user_id} thiếu field {field}"
            print(f"      - {field}: ✅")

    print("\n✅ DATABASE INTEGRITY: PASS")

def run_all_tests():
    """Chạy tất cả tests"""
    print("=" * 60)
    print("  CUPID AGENT - TEST SUITE")
    print("=" * 60)

    try:
        test_get_personality_profile()
        test_calculate_compatibility()
        test_search_matches()
        test_get_relationship_advice()
        test_database_integrity()

        print("\n" + "="*60)
        print("🎉 TẤT CẢ TESTS ĐỀU PASS!")
        print("="*60)
        print("\n✅ Tools đã sẵn sàng để tích hợp vào ReAct Agent!")

    except AssertionError as e:
        print("\n" + "="*60)
        print("❌ TEST FAILED!")
        print("="*60)
        print(f"Lỗi: {e}")
        sys.exit(1)
    except Exception as e:
        print("\n" + "="*60)
        print("💥 UNEXPECTED ERROR!")
        print("="*60)
        print(f"Lỗi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_all_tests()
