"""Tầng 0 (cổng an toàn) và Tầng 1 (bộ lọc cứng) của engine ghép đôi.

Nguyên tắc: mọi điều kiện ở đây là NHỊ PHÂN — đạt hoặc không. Không có
"điểm thấp" thay cho "bị chặn". Ghép hai người có ý định mâu thuẫn nền tảng
hoặc vi phạm deal-breaker gây tổn thương thật, nên chúng bị loại hẳn khỏi
tập ứng viên thay vì bị xếp hạng thấp.

Bộ lọc luôn HAI CHIỀU: A phải hợp tiêu chí của B và B phải hợp tiêu chí của A.
Đây là điểm khác biệt cốt lõi giữa reciprocal recommendation và recsys thường.
"""

import math

from . import schema


def haversine_km(loc_a, loc_b):
    """Khoảng cách đường chim bay giữa hai toạ độ, đơn vị km.

    Trả về None nếu thiếu toạ độ — caller phải coi đây là "không xác định"
    chứ không phải "khoảng cách bằng 0".
    """
    try:
        lat1, lon1 = float(loc_a["lat"]), float(loc_a["lon"])
        lat2, lon2 = float(loc_b["lat"]), float(loc_b["lon"])
    except (KeyError, TypeError, ValueError):
        return None

    radius = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(d_lon / 2) ** 2)
    return radius * 2 * math.asin(math.sqrt(a))


def safety_gate(profile_a, profile_b):
    """Tầng 0 — điều kiện an toàn không thương lượng.

    Trả về tuple lý do bị chặn (rỗng = qua cổng).
    """
    blocks = []

    for profile in (profile_a, profile_b):
        age = profile.get("age")
        if not isinstance(age, int) or age < schema.MIN_AGE:
            blocks.append(
                f"{profile.get('user_id')}: không đạt độ tuổi tối thiểu "
                f"{schema.MIN_AGE} — chặn cứng."
            )
        if profile.get("blocked") is True:
            blocks.append(f"{profile.get('user_id')}: tài khoản đang bị khoá.")

    blocked_list_a = profile_a.get("blocked_users", []) or []
    blocked_list_b = profile_b.get("blocked_users", []) or []
    if profile_b.get("user_id") in blocked_list_a or profile_a.get("user_id") in blocked_list_b:
        blocks.append("Hai người dùng đã chặn nhau.")

    return tuple(blocks)


def hard_filters(profile_a, profile_b, overrides=None):
    """Tầng 1 — bộ lọc cứng hai chiều.

    `overrides` cho phép nới lỏng tiêu chí của A khi lượt tìm trước trả về 0
    kết quả (agent tự quyết định nới gì). Chỉ áp cho A, không đụng tiêu chí
    của B — không ai được nới lỏng ranh giới của người khác.

    Trả về (passed: bool, reasons: tuple[str]).
    """
    reasons = list(safety_gate(profile_a, profile_b))
    if reasons:
        return False, tuple(reasons)

    prefs_a = _effective_preferences(profile_a, overrides)
    prefs_b = profile_b.get("preferences", {}) or {}

    reasons.extend(_check_orientation(profile_a, profile_b))
    reasons.extend(_check_age(profile_a, profile_b, prefs_a, prefs_b))
    reasons.extend(_check_distance(profile_a, profile_b, prefs_a, prefs_b))
    reasons.extend(_check_intent(profile_a, profile_b, prefs_a, prefs_b))
    reasons.extend(_check_status_conflict(profile_a, profile_b))
    reasons.extend(_check_deal_breakers(profile_a, profile_b, overrides))

    return (not reasons), tuple(reasons)


def _effective_preferences(profile, overrides):
    """Ghép preferences gốc với phần nới lỏng — trả về dict MỚI, không sửa gốc."""
    base = dict(profile.get("preferences", {}) or {})
    if overrides:
        base.update(overrides)
    return base


def _check_orientation(profile_a, profile_b):
    """Giới tính/xu hướng phải khớp HAI CHIỀU."""
    gender_a, gender_b = profile_a.get("gender"), profile_b.get("gender")
    wants_a = profile_a.get("interested_in", []) or []
    wants_b = profile_b.get("interested_in", []) or []

    problems = []
    if gender_b not in wants_a:
        problems.append(
            f"{profile_a.get('user_id')} không tìm kiếm giới tính "
            f"{schema.label(gender_b)}."
        )
    if gender_a not in wants_b:
        problems.append(
            f"{profile_b.get('user_id')} không tìm kiếm giới tính "
            f"{schema.label(gender_a)}."
        )
    return problems


def _check_age(profile_a, profile_b, prefs_a, prefs_b):
    """Tuổi phải nằm trong khoảng mong muốn của cả hai phía."""
    problems = []
    age_a, age_b = profile_a.get("age"), profile_b.get("age")

    if not _age_in_range(age_b, prefs_a):
        problems.append(
            f"Tuổi {age_b} nằm ngoài khoảng mong muốn của "
            f"{profile_a.get('user_id')} ({prefs_a.get('age_min')}-{prefs_a.get('age_max')})."
        )
    if not _age_in_range(age_a, prefs_b):
        problems.append(
            f"Tuổi {age_a} nằm ngoài khoảng mong muốn của "
            f"{profile_b.get('user_id')} ({prefs_b.get('age_min')}-{prefs_b.get('age_max')})."
        )
    return problems


def _age_in_range(age, prefs):
    if not isinstance(age, int):
        return False
    low = prefs.get("age_min", schema.MIN_AGE)
    high = prefs.get("age_max", 120)
    return low <= age <= high


def _check_distance(profile_a, profile_b, prefs_a, prefs_b):
    """Khoảng cách phải nằm trong bán kính CHẶT HƠN của hai phía."""
    distance = haversine_km(profile_a.get("location", {}), profile_b.get("location", {}))
    if distance is None:
        return ["Không xác định được khoảng cách (thiếu toạ độ)."]

    limit_a = prefs_a.get("max_distance_km")
    limit_b = prefs_b.get("max_distance_km")
    limits = [value for value in (limit_a, limit_b) if isinstance(value, (int, float))]
    if not limits:
        return []

    tightest = min(limits)
    if distance > tightest:
        return [f"Khoảng cách {distance:.1f} km vượt bán kính tối đa {tightest} km."]
    return []


def _check_intent(profile_a, profile_b, prefs_a, prefs_b):
    """Ý định mâu thuẫn nền tảng (ô 0 trong ma trận) là chặn cứng."""
    intent_a, intent_b = profile_a.get("intent"), profile_b.get("intent")
    row = schema.INTENT_MATRIX.get(intent_a, {})
    if intent_b not in row:
        return [f"Không đánh giá được ý định: {intent_a} / {intent_b}."]

    if row[intent_b] == 0:
        return [
            f"Ý định mâu thuẫn nền tảng: {schema.label(intent_a)} "
            f"vs {schema.label(intent_b)}."
        ]

    # Danh sách ý định chấp nhận được, nếu người dùng khai tường minh.
    # Lấy từ prefs đã áp override để phương án nới lỏng có hiệu lực.
    accepted_a = prefs_a.get("accepted_intents")
    accepted_b = prefs_b.get("accepted_intents")
    problems = []
    if accepted_a and intent_b not in accepted_a:
        problems.append(
            f"{profile_a.get('user_id')} không chấp nhận ý định "
            f"{schema.label(intent_b)}."
        )
    if accepted_b and intent_a not in accepted_b:
        problems.append(
            f"{profile_b.get('user_id')} không chấp nhận ý định "
            f"{schema.label(intent_a)}."
        )
    return problems


def _check_status_conflict(profile_a, profile_b):
    """Đang trong mối quan hệ cam kết nhưng tìm quan hệ độc quyền.

    Không phải chuyện đạo đức của engine, mà là bảo vệ phía còn lại khỏi
    bước vào một tình huống họ không đồng thuận.
    """
    problems = []
    for actor, other in ((profile_a, profile_b), (profile_b, profile_a)):
        status = actor.get("relationship_status")
        if status in schema.COMMITTED_STATUS and other.get("intent") in schema.EXCLUSIVE_INTENTS:
            problems.append(
                f"{actor.get('user_id')} đang ở trạng thái "
                f"{schema.label(status)} trong khi {other.get('user_id')} tìm "
                f"{schema.label(other.get('intent'))} — xung đột cam kết."
            )
    return problems


def _check_deal_breakers(profile_a, profile_b, overrides=None):
    """Deal-breaker = trường gắn MANDATORY. Kiểm tra hai chiều.

    Chỉ deal-breaker của A mới có thể được nới lỏng qua overrides; của B thì
    không — người dùng không được phép bỏ qua ranh giới của đối phương.
    """
    relaxed = set((overrides or {}).get("drop_deal_breakers", []))

    problems = []
    for actor, other, allow_relax in ((profile_a, profile_b, True), (profile_b, profile_a, False)):
        breakers = actor.get("deal_breakers", {}) or {}
        lifestyle = other.get("lifestyle", {}) or {}
        for field, allowed in breakers.items():
            if allow_relax and field in relaxed:
                continue
            value = lifestyle.get(field, other.get(field))
            if value is not None and value not in allowed:
                problems.append(
                    f"{actor.get('user_id')} đặt deal-breaker '{field}' "
                    f"(chấp nhận: {allowed}) nhưng {other.get('user_id')} là "
                    f"'{schema.label(value)}'."
                )
    return problems
