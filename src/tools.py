"""
🛠️ TOOL REGISTRY & SCHEMAS (Dành cho Role 2: Tool & Spec Engineer)
Nơi khai báo tất cả các "món đồ nghề" mà ReAct Agent có thể gọi.

🎯 CHỦ ĐỀ: CUPID AGENT - TRỢ LÝ GHÉP ĐÔI & PHÂN TÍCH ĐỘ TƯƠNG THÍCH
📊 DATABASE: Sử dụng dữ liệu THỰC TẾ từ file JSON (30+ users realistic)
"""

import json
import os

# ===== LOAD DATABASE THỰC TẾ TỪ FILE JSON =====
def load_user_database():
    """Load database từ file JSON"""
    # Tìm file data
    possible_paths = [
        "data/users_realistic.json",
        "../data/users_realistic.json",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "users_realistic.json")
    ]

    for path in possible_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)

    # Fallback: Nếu không tìm thấy file, dùng data mẫu nhỏ
    print("Warning: Could not find users_realistic.json, using fallback data")
    return {
        "minh": {
            "name": "Minh",
            "age": 25,
            "gender": "Nam",
            "personality": "Huong ngoai, Thich phieu luu, Nang dong",
            "interests": ["Du lich", "The thao", "Am nhac", "Nau an"],
            "zodiac": "Bach Duong",
            "relationship_status": "Doc than",
            "looking_for": "Nu, 22-28 tuoi"
        }
    }

# Load database khi import module
USER_DATABASE = load_user_database()

print(f"Loaded {len(USER_DATABASE)} users from realistic database")

# ===== MA TRẬN TƯƠNG THÍCH CUNG HOÀNG ĐẠO =====
ZODIAC_COMPATIBILITY = {
    ("Bach Duong", "Su Tu"): 90,
    ("Bach Duong", "Nhan Ma"): 85,
    ("Su Tu", "Bach Duong"): 90,
    ("Su Tu", "Nhan Ma"): 88,
    ("Xu Nu", "Song Ngu"): 75,
    ("Song Ngu", "Xu Nu"): 75,
    ("Nhan Ma", "Bach Duong"): 85,
    ("Nhan Ma", "Su Tu"): 88,
    ("Kim Nguu", "Ma Ket"): 80,
    ("Ma Ket", "Kim Nguu"): 80,
    ("Song Tu", "Thien Binh"): 85,
    ("Thien Binh", "Song Tu"): 85,
    ("Cu Giai", "Thien Yet"): 70,
    ("Thien Yet", "Cu Giai"): 70,
    ("Bao Binh", "Song Tu"): 82,
    ("Song Tu", "Bao Binh"): 82,
    ("Bo Cap", "Nhan Ma"): 75,
    ("Nhan Ma", "Bo Cap"): 75,
}

# Danh sách 12 cung hoàng đạo hợp lệ
VALID_ZODIACS = {
    "Bach Duong", "Kim Nguu", "Song Tu", "Cu Giai",
    "Su Tu", "Xu Nu", "Thien Binh", "Thien Yet",
    "Nhan Ma", "Ma Ket", "Bao Binh", "Song Ngu", "Bo Cap"
}

# ===== MA TRẬN TƯƠNG THÍCH MBTI =====
MBTI_COMPATIBILITY = {
    ("INTJ", "ENFP"): 85,
    ("ENFP", "INTJ"): 85,
    ("INTJ", "ENTP"): 80,
    ("ENTP", "INTJ"): 80,
    ("INFJ", "ENFP"): 88,
    ("ENFP", "INFJ"): 88,
    ("INFP", "ENFJ"): 82,
    ("ENFJ", "INFP"): 82,
    ("ISTJ", "ESFP"): 70,
    ("ESFP", "ISTJ"): 70,
    ("ISTP", "ESFJ"): 65,
    ("ESFJ", "ISTP"): 65,
    ("INTP", "ENTJ"): 78,
    ("ENTJ", "INTP"): 78,
    ("ISFJ", "ESTP"): 72,
    ("ESTP", "ISFJ"): 72,
    ("ISFP", "ESTJ"): 68,
    ("ESTJ", "ISFP"): 68,
}

# Danh sách 16 kiểu MBTI hợp lệ
VALID_MBTI = {
    "INTJ", "INTP", "ENTJ", "ENTP",
    "INFJ", "INFP", "ENFJ", "ENFP",
    "ISTJ", "ISFJ", "ESTJ", "ESFJ",
    "ISTP", "ISFP", "ESTP", "ESFP"
}


def get_personality_profile(user_id: str) -> str:
    """
    Lấy hồ sơ tính cách và sở thích của một người dùng.

    Args:
        user_id (str): ID hoặc tên người dùng (Ví dụ: 'minh', 'linh', 'huy')

    Returns:
        str: Thông tin chi tiết về hồ sơ cá nhân, tính cách, sở thích

    Error Handling:
        Trả về thông báo lỗi nếu không tìm thấy user_id
    """
    user_id_lower = user_id.lower().strip()

    if user_id_lower not in USER_DATABASE:
        return f"LỖI: Không tìm thấy hồ sơ người dùng '{user_id}'. Các user hợp lệ: {', '.join(USER_DATABASE.keys())}."

    profile = USER_DATABASE[user_id_lower]
    interests_str = ", ".join(profile["interests"])

    return (
        f"👤 Hồ sơ của {profile['name']}:\n"
        f"   • Tuổi: {profile['age']}\n"
        f"   • Giới tính: {profile['gender']}\n"
        f"   • Tính cách: {profile['personality']}\n"
        f"   • Sở thích: {interests_str}\n"
        f"   • Cung hoàng đạo: {profile['zodiac']}\n"
        f"   • Tình trạng: {profile['relationship_status']}\n"
        f"   • Đang tìm kiếm: {profile['looking_for']}"
    )


def calculate_compatibility(user1_id: str, user2_id: str) -> str:
    """
    Tính điểm tương thích giữa hai người dựa trên tính cách, sở thích và cung hoàng đạo.

    Args:
        user1_id (str): ID người thứ nhất (Ví dụ: 'minh')
        user2_id (str): ID người thứ hai (Ví dụ: 'linh')

    Returns:
        str: Điểm tương thích (0-100) và phân tích chi tiết

    Error Handling:
        Trả về thông báo lỗi nếu không tìm thấy một trong hai user_id
    """
    user1_id_lower = user1_id.lower().strip()
    user2_id_lower = user2_id.lower().strip()

    if user1_id_lower not in USER_DATABASE:
        return f"LỖI: Không tìm thấy người dùng '{user1_id}'."
    if user2_id_lower not in USER_DATABASE:
        return f"LỖI: Không tìm thấy người dùng '{user2_id}'."

    user1 = USER_DATABASE[user1_id_lower]
    user2 = USER_DATABASE[user2_id_lower]

    # Tính điểm dựa trên sở thích chung
    common_interests = set(user1["interests"]) & set(user2["interests"])
    interest_score = len(common_interests) * 15  # Mỗi sở thích chung: +15 điểm

    # Tính điểm dựa trên cung hoàng đạo
    zodiac_pair = (user1["zodiac"], user2["zodiac"])
    zodiac_score = ZODIAC_COMPATIBILITY.get(zodiac_pair, 50)  # Mặc định 50 nếu không có data

    # Tính điểm tổng hợp
    total_score = min(100, (interest_score + zodiac_score) // 2)

    # Đánh giá mức độ tương thích
    if total_score >= 80:
        level = "Rất cao ❤️❤️❤️"
    elif total_score >= 60:
        level = "Cao ❤️❤️"
    elif total_score >= 40:
        level = "Trung bình ❤️"
    else:
        level = "Thấp 💔"

    common_interests_str = ", ".join(common_interests) if common_interests else "Không có"

    return (
        f"💕 Phân tích độ tương thích giữa {user1['name']} và {user2['name']}:\n"
        f"   • Điểm tổng hợp: {total_score}/100\n"
        f"   • Mức độ: {level}\n"
        f"   • Sở thích chung: {common_interests_str}\n"
        f"   • Điểm sở thích: {interest_score}/100\n"
        f"   • Điểm cung hoàng đạo ({user1['zodiac']} - {user2['zodiac']}): {zodiac_score}/100"
    )


def search_matches(user_id: str, min_compatibility: int = 60) -> str:
    """
    Tìm kiếm những người phù hợp nhất với một người dùng.

    Args:
        user_id (str): ID người dùng cần tìm đối tượng (Ví dụ: 'minh')
        min_compatibility (int): Điểm tương thích tối thiểu (mặc định 60)

    Returns:
        str: Danh sách những người phù hợp được sắp xếp theo điểm tương thích

    Error Handling:
        Trả về thông báo lỗi nếu không tìm thấy user_id
    """
    user_id_lower = user_id.lower().strip()
    min_compatibility = int(min_compatibility)  # Fix: ép kiểu string → int từ parser

    if user_id_lower not in USER_DATABASE:
        return f"LỖI: Không tìm thấy người dùng '{user_id}'."

    user = USER_DATABASE[user_id_lower]
    matches = []

    for candidate_id, candidate in USER_DATABASE.items():
        if candidate_id == user_id_lower:
            continue  # Bỏ qua chính mình

        # Tính điểm tương thích
        common_interests = set(user["interests"]) & set(candidate["interests"])
        interest_score = len(common_interests) * 15

        zodiac_pair = (user["zodiac"], candidate["zodiac"])
        zodiac_score = ZODIAC_COMPATIBILITY.get(zodiac_pair, 50)

        total_score = min(100, (interest_score + zodiac_score) // 2)

        if total_score >= min_compatibility:
            matches.append({
                "name": candidate["name"],
                "score": total_score,
                "age": candidate["age"],
                "personality": candidate["personality"]
            })

    if not matches:
        return f"Không tìm thấy người phù hợp với điểm tương thích >= {min_compatibility}."

    # Sắp xếp theo điểm giảm dần
    matches.sort(key=lambda x: x["score"], reverse=True)

    result = f"🔍 Tìm thấy {len(matches)} người phù hợp với {user['name']}:\n"
    for i, match in enumerate(matches, 1):
        result += f"   {i}. {match['name']} ({match['age']} tuổi) - Điểm: {match['score']}/100\n"
        result += f"      Tính cách: {match['personality']}\n"

    return result.strip()


def get_relationship_advice(situation: str) -> str:
    """
    Cung cấp lời khuyên về mối quan hệ dựa trên tình huống.

    Args:
        situation (str): Mô tả tình huống (Ví dụ: 'hẹn hò đầu tiên', 'giữ lửa tình yêu')

    Returns:
        str: Lời khuyên chi tiết về mối quan hệ

    Note:
        Tool này là read-only và không thay đổi trạng thái hệ thống
    """
    situation_lower = situation.lower().strip()

    advice_database = {
        "hẹn hò đầu tiên": (
            "💝 Lời khuyên cho buổi hẹn đầu tiên:\n"
            "   1. Chọn địa điểm thoải mái, không quá ồn ào\n"
            "   2. Lắng nghe chủ động và đặt câu hỏi mở\n"
            "   3. Ăn mặc gọn gàng, tự tin nhưng tự nhiên\n"
            "   4. Đừng nói quá nhiều về người yêu cũ\n"
            "   5. Kết thúc buổi hẹn đúng lúc, để lại ấn tượng tốt"
        ),
        "giữ lửa": (
            "🔥 Lời khuyên để giữ lửa tình yêu:\n"
            "   1. Dành thời gian chất lượng cho nhau mỗi tuần\n"
            "   2. Luôn thể hiện sự quan tâm qua hành động nhỏ\n"
            "   3. Giao tiếp cởi mở, chia sẻ cảm xúc thật\n"
            "   4. Tạo bất ngờ và làm mới mối quan hệ\n"
            "   5. Tôn trọng không gian riêng của nhau"
        ),
        "xung đột": (
            "⚖️ Lời khuyên khi có xung đột:\n"
            "   1. Bình tĩnh, không nói khi đang tức giận\n"
            "   2. Lắng nghe quan điểm của người kia trước\n"
            "   3. Tập trung vào vấn đề, không công kích cá nhân\n"
            "   4. Tìm điểm chung và thỏa hiệp\n"
            "   5. Xin lỗi khi sai và tha thứ chân thành"
        )
    }

    for keyword, advice in advice_database.items():
        if keyword in situation_lower:
            return advice

    # Lời khuyên mặc định
    return (
        "💡 Lời khuyên chung cho mối quan hệ:\n"
        "   1. Giao tiếp cởi mở và trung thực\n"
        "   2. Thể hiện sự quan tâm và tôn trọng\n"
        "   3. Duy trì sự cân bằng giữa cho và nhận\n"
        "   4. Xây dựng lòng tin qua thời gian\n"
        "   5. Luôn sẵn sàng học hỏi và phát triển cùng nhau"
    )


def get_zodiac_compatibility(zodiac1: str, zodiac2: str) -> str:
    """
    Tính độ tương thích giữa 2 cung hoàng đạo.

    Args:
        zodiac1 (str): Cung hoàng đạo thứ nhất (Ví dụ: 'Sư Tử', 'Nhân Mã')
        zodiac2 (str): Cung hoàng đạo thứ hai (Ví dụ: 'Bọ Cạp', 'Bạch Dương')

    Returns:
        str: Điểm tương thích và phân tích chi tiết

    Error Handling:
        Trả về thông báo lỗi nếu cung hoàng đạo không hợp lệ
    """
    # Chuẩn hóa input
    z1 = zodiac1.strip()
    z2 = zodiac2.strip()

    # Kiểm tra tính hợp lệ
    if z1 not in VALID_ZODIACS:
        valid_list = ", ".join(sorted(VALID_ZODIACS))
        return f"[LOI] Cung hoang dao '{zodiac1}' khong hop le. Cac cung hop le: {valid_list}"

    if z2 not in VALID_ZODIACS:
        valid_list = ", ".join(sorted(VALID_ZODIACS))
        return f"[LOI] Cung hoang dao '{zodiac2}' khong hop le. Cac cung hop le: {valid_list}"

    # Tra cứu điểm tương thích
    score = ZODIAC_COMPATIBILITY.get((z1, z2), 50)  # Default 50 nếu không có trong ma trận

    # Phân loại mức độ
    if score >= 85:
        level = "Rat cao"
        description = "Hai cung nay co su hoa hop tuyet voi ve tinh cach va quan diem song."
    elif score >= 75:
        level = "Cao"
        description = "Hai cung co nhieu diem chung va de dang hieu nhau."
    elif score >= 60:
        level = "Trung binh"
        description = "Hai cung co the hop nhau neu cung no luc va thau hieu."
    else:
        level = "Thap"
        description = "Hai cung co su khac biet lon, can nhieu su nhan nai va thoa hiep."

    result = f"Do tuong thich giua cung {z1} va cung {z2}:\n"
    result += f"   - Diem so: {score}/100\n"
    result += f"   - Muc do: {level}\n"
    result += f"   - Phan tich: {description}"

    return result


def get_mbti_compatibility(mbti1: str, mbti2: str) -> str:
    """
    Tính độ tương thích giữa 2 kiểu tính cách MBTI.

    Args:
        mbti1 (str): Kiểu MBTI thứ nhất (Ví dụ: 'INTJ', 'ENFP')
        mbti2 (str): Kiểu MBTI thứ hai (Ví dụ: 'INFP', 'ESTJ')

    Returns:
        str: Điểm tương thích và phân tích chi tiết

    Error Handling:
        Trả về thông báo lỗi nếu mã MBTI không hợp lệ
    """
    # Chuẩn hóa input (uppercase)
    m1 = mbti1.strip().upper()
    m2 = mbti2.strip().upper()

    # Kiểm tra tính hợp lệ
    if m1 not in VALID_MBTI:
        valid_list = ", ".join(sorted(VALID_MBTI))
        return f"[LOI] Ma MBTI '{mbti1}' khong hop le. Cac ma hop le: {valid_list}"

    if m2 not in VALID_MBTI:
        valid_list = ", ".join(sorted(VALID_MBTI))
        return f"[LOI] Ma MBTI '{mbti2}' khong hop le. Cac ma hop le: {valid_list}"

    # Tra cứu điểm tương thích
    score = MBTI_COMPATIBILITY.get((m1, m2), 60)  # Default 60 nếu không có trong ma trận

    # Phân loại mức độ
    if score >= 85:
        level = "Rat cao"
        description = "Hai kieu tinh cach nay bo sung hoan hao cho nhau, tao su can bang tuyet voi."
    elif score >= 75:
        level = "Cao"
        description = "Hai kieu tinh cach co nhieu diem tuong dong va de dang ket noi."
    elif score >= 65:
        level = "Trung binh"
        description = "Hai kieu tinh cach co the hoa hop neu cung no luc hieu nhau."
    else:
        level = "Thap"
        description = "Hai kieu tinh cach co su khac biet dang ke, can nhieu su kien nhan."

    result = f"Do tuong thich MBTI giua {m1} va {m2}:\n"
    result += f"   - Diem so: {score}/100\n"
    result += f"   - Muc do: {level}\n"
    result += f"   - Phan tich: {description}"

    return result


# ===== DANH SÁCH CÁC TOOL ĐƯỢC ĐĂNG KÝ =====
AVAILABLE_TOOLS = {
    "get_personality_profile": get_personality_profile,
    "calculate_compatibility": calculate_compatibility,
    "search_matches": search_matches,
    "get_relationship_advice": get_relationship_advice,
    "get_zodiac_compatibility": get_zodiac_compatibility,
    "get_mbti_compatibility": get_mbti_compatibility,
}
