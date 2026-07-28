"""Nạp, kiểm định và chiếu (project) hồ sơ người dùng.

Điểm quan trọng về an toàn: `public_view()` là hàng rào PII ở TẦNG DỮ LIỆU.
Mọi thứ trong khối `private` (số điện thoại, địa chỉ chính xác) không bao giờ
rời khỏi module này. Guardrail ở prompt có thể bị vượt qua bằng prompt
injection; hàng rào ở tầng dữ liệu thì không, vì dữ liệu nhạy cảm đơn giản là
chưa từng đi vào context của LLM.
"""

import json
import os

from . import schema

# Khối dữ liệu không bao giờ được trả ra ngoài engine.
PRIVATE_KEY = "private"

# Thuộc tính nhạy cảm: được phép dùng để chấm điểm cho CHÍNH chủ hồ sơ,
# nhưng không được tiết lộ cho người thứ ba trong phần diễn giải.
SENSITIVE_FIELDS = ("orientation", "drugs", "relationship_status", "religion", "ethnicity")

_DEFAULT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "config", "profiles.json",
)


def load_profiles(path=None):
    """Đọc kho hồ sơ từ JSON, trả về dict {user_id: profile}.

    Luôn mở bằng encoding utf-8 tường minh — mặc định của Windows là cp1252
    và sẽ làm hỏng tiếng Việt có dấu.
    """
    target = path or _DEFAULT_PATH
    if not os.path.exists(target):
        raise FileNotFoundError(f"Không tìm thấy kho hồ sơ tại: {target}")

    with open(target, "r", encoding="utf-8") as handle:
        raw = json.load(handle)

    if not isinstance(raw, list):
        raise ValueError("profiles.json phải là một mảng các hồ sơ.")

    return {item["user_id"]: item for item in raw}


def get_profile(profiles, user_id):
    """Lấy 1 hồ sơ. Trả về None nếu không tồn tại (caller tự sinh thông báo lỗi)."""
    return profiles.get(user_id)


def public_view(profile, viewer_is_owner=False):
    """Trả về BẢN SAO hồ sơ đã loại bỏ dữ liệu riêng tư.

    Không bao giờ sửa đổi `profile` gốc. Nếu người xem chính là chủ hồ sơ,
    vẫn loại bỏ khối `private` — engine không có nhu cầu đọc nó, và giữ nguyên
    quy tắc này giúp tránh rò rỉ do nhầm lẫn về sau.
    """
    del viewer_is_owner  # giữ tham số cho rõ ý định; hiện luôn lọc như nhau
    return {key: value for key, value in profile.items() if key != PRIVATE_KEY}


def summary_card(profile):
    """Bản tóm tắt tối thiểu để đưa vào shortlist — chỉ những gì cần để chọn.

    Cố ý KHÔNG chứa xu hướng tính dục, tình trạng dùng chất hay tôn giáo:
    đó là thuộc tính nhạy cảm, chỉ dùng để lọc/chấm chứ không phơi ra danh sách.
    """
    location = profile.get("location", {})
    socio = profile.get("socio", {})
    return {
        "user_id": profile.get("user_id"),
        "display_name": profile.get("display_name"),
        "age": profile.get("age"),
        "city": location.get("city"),
        "district": location.get("district"),
        "occupation": socio.get("occupation"),
        "intent": profile.get("intent"),
    }


def validate_profile(profile):
    """Kiểm định hồ sơ, trả về tuple các thông báo lỗi (rỗng nếu hợp lệ).

    Bắt cả lỗi thiếu trường lẫn MÂU THUẪN nội tại — ví dụ khai "dị tính"
    nhưng `interested_in` lại trùng giới tính của chính mình. Hồ sơ mâu thuẫn
    là dấu hiệu người dùng nhập ẩu hoặc đang cố lách bộ lọc.
    """
    errors = []

    for field in ("user_id", "age", "gender", "orientation", "interested_in", "intent"):
        if profile.get(field) in (None, "", []):
            errors.append(f"Thiếu trường bắt buộc: {field}")

    age = profile.get("age")
    if isinstance(age, int):
        if age < schema.MIN_AGE:
            errors.append(
                f"Người dùng dưới {schema.MIN_AGE} tuổi (khai {age}) — "
                "không đủ điều kiện sử dụng dịch vụ ghép đôi."
            )
        elif age > 120:
            errors.append(f"Tuổi không hợp lệ: {age}")
    elif age is not None:
        errors.append("Trường 'age' phải là số nguyên.")

    gender = profile.get("gender")
    if gender is not None and gender not in schema.GENDERS:
        errors.append(f"Giới tính không hợp lệ: {gender}")

    orientation = profile.get("orientation")
    if orientation is not None and orientation not in schema.ORIENTATIONS:
        errors.append(f"Xu hướng tính dục không hợp lệ: {orientation}")

    intent = profile.get("intent")
    if intent is not None and intent not in schema.INTENTS:
        errors.append(f"Ý định quan hệ không hợp lệ: {intent}")

    status = profile.get("relationship_status")
    if status is not None and status not in schema.RELATIONSHIP_STATUS:
        errors.append(f"Tình trạng mối quan hệ không hợp lệ: {status}")

    interested_in = profile.get("interested_in") or []
    if not isinstance(interested_in, list):
        errors.append("Trường 'interested_in' phải là danh sách.")
    else:
        for item in interested_in:
            if item not in schema.GENDERS:
                errors.append(f"Giá trị 'interested_in' không hợp lệ: {item}")

    errors.extend(_orientation_consistency(profile, interested_in))

    mbti = profile.get("psycho", {}).get("mbti")
    if mbti is not None and not _is_valid_mbti(mbti):
        errors.append(f"Mã MBTI không hợp lệ: {mbti}")

    prefs = profile.get("preferences", {})
    age_min, age_max = prefs.get("age_min"), prefs.get("age_max")
    if isinstance(age_min, int) and isinstance(age_max, int) and age_min > age_max:
        errors.append(f"Khoảng tuổi mong muốn ngược: {age_min} > {age_max}")
    if isinstance(age_min, int) and age_min < schema.MIN_AGE:
        errors.append(
            f"Khoảng tuổi mong muốn bắt đầu từ {age_min}, dưới mức tối thiểu "
            f"{schema.MIN_AGE} — không được phép."
        )

    return tuple(errors)


def _orientation_consistency(profile, interested_in):
    """Đối chiếu xu hướng đã khai với danh sách giới tính quan tâm."""
    gender = profile.get("gender")
    orientation = profile.get("orientation")
    if not gender or not orientation or not interested_in:
        return ()

    same = gender in interested_in
    other = any(item != gender for item in interested_in)

    if orientation == "di_tinh" and same:
        return (f"Mâu thuẫn: khai dị tính nhưng 'interested_in' chứa {gender}.",)
    if orientation == "dong_tinh" and other:
        return ("Mâu thuẫn: khai đồng tính nhưng 'interested_in' chứa giới tính khác.",)
    if orientation in ("song_tinh", "toan_tinh") and not (same and other):
        return ("Mâu thuẫn: khai song/toàn tính nhưng 'interested_in' chỉ có một giới.",)
    return ()


def _is_valid_mbti(code):
    """Kiểm tra mã MBTI 4 chữ cái theo đúng từng cặp đối lập."""
    if not isinstance(code, str) or len(code) != 4:
        return False
    upper = code.upper()
    return all(upper[index] in pair for index, pair in enumerate(schema.MBTI_LETTERS))
