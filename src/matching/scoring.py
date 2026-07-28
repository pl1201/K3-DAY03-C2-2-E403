"""Tầng 2 — chấm điểm mềm và tổng hợp độ tương thích.

Công thức:

    S(A→B) = Σ(wᵢ × matchᵢ(A.pref, B.value)) / Σ(wᵢ)
    Tương thích = √( S(A→B) × S(B→A) ) × 100

Dùng TRUNG BÌNH NHÂN chứ không phải trung bình cộng: ghép đôi chỉ thành công
khi cả hai phía cùng muốn. A chấm B 95 nhưng B chấm A 20 thì trung bình nhân
cho 43 (đúng bản chất: một chiều), trong khi trung bình cộng cho 57 (che mất
sự lệch). Đây cũng là cách công thức match% công khai của OkCupid hoạt động.
"""

import math

from . import filters, schema

# Điểm khi thiếu dữ liệu: hơi tích cực chứ không phải 0. Thiếu thông tin
# không đồng nghĩa với không hợp — phạt nặng sẽ khiến hồ sơ mới luôn bị chìm.
NEUTRAL = 0.70


def compatibility(profile_a, profile_b):
    """Tính độ tương thích đầy đủ giữa hai hồ sơ.

    Trả về dict gồm điểm tổng, nhãn diễn giải, điểm hai chiều và bảng phân rã
    theo từng trục. Giả định caller đã chạy `filters.hard_filters` — hàm này
    chỉ chấm điểm, không tự loại.
    """
    score_ab, breakdown_ab = one_sided_satisfaction(profile_a, profile_b)
    score_ba, _ = one_sided_satisfaction(profile_b, profile_a)

    total = math.sqrt(score_ab * score_ba) * 100

    return {
        "user_id_a": profile_a.get("user_id"),
        "user_id_b": profile_b.get("user_id"),
        "score": round(total, 1),
        "band": _band(total),
        "score_a_to_b": round(score_ab * 100, 1),
        "score_b_to_a": round(score_ba * 100, 1),
        "asymmetry": round(abs(score_ab - score_ba) * 100, 1),
        "breakdown": breakdown_ab,
        "flags": _relationship_flags(profile_a, profile_b),
        "conversation_starters": _conversation_starters(profile_a, profile_b),
    }


def one_sided_satisfaction(actor, other):
    """Mức độ `actor` hài lòng với `other`, trong [0, 1].

    Trả về (điểm, bảng phân rã). Trọng số lấy từ actor.weights, fallback về
    DEFAULT_WEIGHTS — mỗi người tự quyết định điều gì quan trọng với mình.
    """
    weights = dict(schema.DEFAULT_WEIGHTS)
    weights.update(actor.get("weights", {}) or {})

    scorers = {
        "intent": score_intent,
        "distance": score_distance,
        "lifestyle": score_lifestyle,
        "education": score_education,
        "career": score_career,
        "personality": score_personality,
        "interests": score_interests,
        "family": score_family,
    }

    weighted_sum = 0.0
    weight_total = 0.0
    breakdown = []

    for dimension in schema.SCORING_DIMENSIONS:
        weight = weights.get(dimension, 0)
        if weight <= 0:
            continue
        value, note = scorers[dimension](actor, other)
        weighted_sum += weight * value
        weight_total += weight
        breakdown.append({
            "dimension": dimension,
            "label": schema.label(dimension),
            "score": round(value * 100),
            "weight": weight,
            "note": note,
            "verdict": _verdict(value),
        })

    if weight_total == 0:
        return NEUTRAL, tuple(breakdown)

    return weighted_sum / weight_total, tuple(breakdown)


# --- Bộ chấm theo từng trục -------------------------------------------------

def score_intent(actor, other):
    """Ý định quan hệ — trục có trọng số cao nhất."""
    row = schema.INTENT_MATRIX.get(actor.get("intent"), {})
    raw = row.get(other.get("intent"))
    if raw is None:
        return NEUTRAL, "Không xác định được ý định của một trong hai phía."

    note = f"{schema.label(actor.get('intent'))} ↔ {schema.label(other.get('intent'))}"
    return raw / 100.0, note


def score_distance(actor, other):
    """Khoảng cách với hàm suy giảm, không tuyến tính đơn thuần."""
    distance = filters.haversine_km(actor.get("location", {}), other.get("location", {}))
    if distance is None:
        return NEUTRAL, "Không xác định được khoảng cách."

    limit = actor.get("preferences", {}).get("max_distance_km")
    if not isinstance(limit, (int, float)) or limit <= 0:
        limit = 50.0

    if distance <= schema.DISTANCE_NEAR_KM:
        return 1.0, f"{distance:.1f} km — rất gần"

    ratio = min(distance / limit, 1.0)
    value = 1.0 - (1.0 - schema.DISTANCE_FLOOR) * ratio
    return value, f"{distance:.1f} km (bán kính mong muốn {limit:.0f} km)"


def score_lifestyle(actor, other):
    """Lối sống — kết hợp hai cơ chế khác nhau.

    Rượu/thuốc lá/chất gây nghiện chấm theo PREFERENCE của actor, không theo
    độ giống nhau. Hai người cùng dùng chất nặng không phải là "hợp nhau";
    điều quan trọng là actor có chấp nhận mức đó hay không.

    Vận động/giờ sinh hoạt chấm theo độ tương đồng thứ bậc.
    """
    prefs = actor.get("preferences", {}) or {}
    other_lifestyle = other.get("lifestyle", {}) or {}

    parts = []
    notes = []

    for field in schema.PREFERENCE_DRIVEN_LIFESTYLE:
        value = other_lifestyle.get(field)
        if value is None:
            continue
        accepted = prefs.get(f"{field}_pref")
        if not accepted:
            parts.append(NEUTRAL)
            continue
        matched = value in accepted
        parts.append(1.0 if matched else 0.0)
        if not matched:
            notes.append(f"{field}: {schema.label(value)} ngoài mức chấp nhận")

    actor_lifestyle = actor.get("lifestyle", {}) or {}
    for field, scale in schema.SIMILARITY_LIFESTYLE.items():
        value = _ordinal_similarity(actor_lifestyle.get(field), other_lifestyle.get(field), scale)
        if value is None:
            continue
        parts.append(value)
        if value < 0.5:
            notes.append(
                f"{field}: {schema.label(actor_lifestyle.get(field))} vs "
                f"{schema.label(other_lifestyle.get(field))}"
            )

    if not parts:
        return NEUTRAL, "Thiếu dữ liệu lối sống."

    note = "; ".join(notes) if notes else "Lối sống tương thích"
    return sum(parts) / len(parts), note


def score_education(actor, other):
    """Học vấn — khoảng cách thứ bậc, không phải "cao hơn thì tốt hơn"."""
    rank_a = schema.EDUCATION_RANK.get(actor.get("socio", {}).get("education"))
    rank_b = schema.EDUCATION_RANK.get(other.get("socio", {}).get("education"))
    if rank_a is None or rank_b is None:
        return NEUTRAL, "Thiếu dữ liệu học vấn."

    span = max(schema.EDUCATION_RANK.values()) - min(schema.EDUCATION_RANK.values())
    value = 1.0 - abs(rank_a - rank_b) / span
    note = (f"{schema.label(actor.get('socio', {}).get('education'))} vs "
            f"{schema.label(other.get('socio', {}).get('education'))}")
    return value, note


def score_career(actor, other):
    """Nghề nghiệp & ngôn ngữ — tín hiệu yếu, trọng số mặc định thấp."""
    socio_a = actor.get("socio", {}) or {}
    socio_b = other.get("socio", {}) or {}

    langs_a = set(socio_a.get("languages", []) or [])
    langs_b = set(socio_b.get("languages", []) or [])
    if not langs_a or not langs_b:
        language_score = NEUTRAL
    elif langs_a & langs_b:
        language_score = 1.0
    else:
        language_score = 0.0

    industry_a, industry_b = socio_a.get("industry"), socio_b.get("industry")
    if not industry_a or not industry_b:
        industry_score = NEUTRAL
    else:
        industry_score = 0.85 if industry_a == industry_b else 0.65

    value = 0.6 * language_score + 0.4 * industry_score
    if language_score == 0.0:
        return value, "Không có ngôn ngữ chung — rào cản giao tiếp"
    return value, f"{socio_a.get('occupation', '?')} / {socio_b.get('occupation', '?')}"


def score_personality(actor, other):
    """Tính cách — Big Five là trục chính, MBTI và cung hoàng đạo là phụ.

    Tỷ trọng phản ánh độ tin cậy khoa học: Big Five có giá trị dự báo tốt
    nhất, MBTI yếu hơn nhiều, chiêm tinh thuần giải trí.
    """
    psycho_a = actor.get("psycho", {}) or {}
    psycho_b = other.get("psycho", {}) or {}

    components = []

    big_five = _big_five_similarity(psycho_a.get("big_five"), psycho_b.get("big_five"))
    if big_five is not None:
        components.append((0.55, big_five))

    mbti = _mbti_affinity(psycho_a.get("mbti"), psycho_b.get("mbti"))
    if mbti is not None:
        components.append((0.30, mbti))

    zodiac = _zodiac_affinity(psycho_a.get("zodiac"), psycho_b.get("zodiac"))
    if zodiac is not None:
        components.append((0.15, zodiac))

    if not components:
        return NEUTRAL, "Thiếu dữ liệu tính cách."

    total_weight = sum(weight for weight, _ in components)
    value = sum(weight * score for weight, score in components) / total_weight

    note_parts = []
    if psycho_a.get("mbti") and psycho_b.get("mbti"):
        note_parts.append(f"MBTI {psycho_a['mbti']} ↔ {psycho_b['mbti']}")
    if big_five is not None:
        note_parts.append(f"Big Five tương đồng {round(big_five * 100)}%")
    return value, "; ".join(note_parts) or "Đã chấm theo dữ liệu sẵn có"


def score_interests(actor, other):
    """Sở thích & giá trị sống — hệ số Jaccard trên tập hợp."""
    psycho_a = actor.get("psycho", {}) or {}
    psycho_b = other.get("psycho", {}) or {}

    interests = _jaccard(psycho_a.get("interests"), psycho_b.get("interests"))
    values = _jaccard(psycho_a.get("values"), psycho_b.get("values"))

    parts = [item for item in (interests, values) if item is not None]
    if not parts:
        return NEUTRAL, "Thiếu dữ liệu sở thích."

    shared = sorted(set(psycho_a.get("interests") or []) & set(psycho_b.get("interests") or []))
    note = f"Cùng thích: {', '.join(shared)}" if shared else "Chưa tìm thấy sở thích chung"

    # Jaccard thuần rất khắt khe khi hai tập lớn; kéo lên nền 0.35 để một
    # điểm chung vẫn có ý nghĩa thay vì bị coi như hoàn toàn lệch nhau.
    raw = sum(parts) / len(parts)
    return 0.35 + 0.65 * raw, note


def score_family(actor, other):
    """Kế hoạch con cái — trục âm thầm phá vỡ nhiều mối quan hệ dài hạn."""
    plan_a = actor.get("family", {}).get("wants_children")
    plan_b = other.get("family", {}).get("wants_children")

    if plan_a is None or plan_b is None:
        return NEUTRAL, "Thiếu dữ liệu kế hoạch gia đình."
    if plan_a == plan_b == "chua_xac_dinh":
        return 0.75, "Cả hai đều chưa xác định"
    if plan_a == plan_b:
        return 1.0, f"Cả hai {schema.label(plan_a).lower()}"
    if "chua_xac_dinh" in (plan_a, plan_b):
        return 0.60, f"{schema.label(plan_a)} vs {schema.label(plan_b)}"
    return 0.0, f"Xung đột: {schema.label(plan_a)} vs {schema.label(plan_b)}"


# --- Hàm phụ trợ ------------------------------------------------------------

def _ordinal_similarity(value_a, value_b, scale):
    """Độ tương đồng trên thang thứ bậc, trả None nếu thiếu dữ liệu."""
    rank_a, rank_b = scale.get(value_a), scale.get(value_b)
    if rank_a is None or rank_b is None:
        return None
    span = max(scale.values()) - min(scale.values())
    if span == 0:
        return 1.0
    return 1.0 - abs(rank_a - rank_b) / span


def _big_five_similarity(traits_a, traits_b):
    """1 − sai khác trung bình tuyệt đối, chuẩn hoá về [0, 1]."""
    if not traits_a or not traits_b:
        return None
    diffs = []
    for trait in schema.BIG_FIVE_TRAITS:
        value_a, value_b = traits_a.get(trait), traits_b.get(trait)
        if isinstance(value_a, (int, float)) and isinstance(value_b, (int, float)):
            diffs.append(abs(value_a - value_b) / 100.0)
    if not diffs:
        return None
    return 1.0 - sum(diffs) / len(diffs)


def _mbti_affinity(code_a, code_b):
    """Heuristic MBTI theo từng cặp chữ cái (xem schema.MBTI_RULES)."""
    if not code_a or not code_b or len(code_a) != 4 or len(code_b) != 4:
        return None
    upper_a, upper_b = code_a.upper(), code_b.upper()

    total = 0.0
    for index, same_score, diff_score in schema.MBTI_RULES:
        total += same_score if upper_a[index] == upper_b[index] else diff_score
    return min(total, 1.0)


def _zodiac_affinity(sign_a, sign_b):
    """Tương hợp theo nguyên tố chiêm tinh — tín hiệu giải trí, trọng số thấp."""
    element_a = schema.ZODIAC_ELEMENT.get(sign_a)
    element_b = schema.ZODIAC_ELEMENT.get(sign_b)
    if not element_a or not element_b:
        return None
    key = (element_a, element_b)
    if key not in schema.ELEMENT_AFFINITY:
        key = (element_b, element_a)
    return schema.ELEMENT_AFFINITY.get(key, 0.5)


def _jaccard(list_a, list_b):
    """|A ∩ B| / |A ∪ B|, None nếu một trong hai tập rỗng."""
    set_a, set_b = set(list_a or []), set(list_b or [])
    if not set_a or not set_b:
        return None
    union = set_a | set_b
    return len(set_a & set_b) / len(union)


def _band(total):
    for threshold, name in schema.SCORE_BANDS:
        if total >= threshold:
            return name
    return schema.SCORE_BANDS[-1][1]


def _verdict(value):
    if value >= 0.80:
        return "tot"
    if value >= 0.55:
        return "kha"
    return "luu_y"


def _relationship_flags(profile_a, profile_b):
    """Cảnh báo cần nói thẳng với người dùng, kể cả khi điểm tổng cao."""
    flags = []

    plan_a = profile_a.get("family", {}).get("wants_children")
    plan_b = profile_b.get("family", {}).get("wants_children")
    if {plan_a, plan_b} == {"muon", "khong_muon"}:
        flags.append("Kế hoạch con cái đối lập — nên trao đổi sớm.")

    intent_score = schema.INTENT_MATRIX.get(
        profile_a.get("intent"), {}).get(profile_b.get("intent"), 100)
    if intent_score < 60:
        flags.append("Mức độ nghiêm túc mong muốn khác nhau đáng kể.")

    for actor, other in ((profile_a, profile_b), (profile_b, profile_a)):
        if actor.get("relationship_status") in schema.COMMITTED_STATUS:
            flags.append(
                f"{actor.get('user_id')} đang trong một mối quan hệ — "
                f"{other.get('user_id')} cần biết điều này."
            )

    return tuple(flags)


def _conversation_starters(profile_a, profile_b):
    """Gợi ý mở lời dựa trên điểm chung có thật, không bịa."""
    interests_a = set(profile_a.get("psycho", {}).get("interests") or [])
    interests_b = set(profile_b.get("psycho", {}).get("interests") or [])
    shared = sorted(interests_a & interests_b)

    starters = [f"Cả hai cùng quan tâm {topic} — thử bắt đầu từ đó." for topic in shared[:2]]

    city_a = profile_a.get("location", {}).get("city")
    city_b = profile_b.get("location", {}).get("city")
    if city_a and city_a == city_b:
        starters.append(f"Cùng ở {city_a}, dễ hẹn gặp trực tiếp.")

    return tuple(starters)
