"""Điều phối 3 tầng: cổng an toàn → lọc cứng → chấm điểm → xếp hạng.

Đây là lớp mà Role 2 sẽ bọc thành Tool cho ReAct Agent. Mọi hàm ở đây trả về
dict/tuple thuần Python, không in ra màn hình và không gọi LLM — nhờ vậy có
thể kiểm thử tất định, và bản thân engine miễn nhiễm với prompt injection
nằm trong dữ liệu hồ sơ.

Điểm thiết kế đáng chú ý: khi `search_candidates` trả về 0 ứng viên, nó kèm
theo `relaxation_hints` — các phương án nới lỏng KHẢ THI kèm số ứng viên sẽ
mở ra. Agent tự chọn nới cái nào rồi gọi lại. Đó là chỗ vòng lặp ReAct thực
sự cần thiết, thay vì một kịch bản cố định.
"""

from . import filters, profiles as profiles_mod, scoring

DEFAULT_LIMIT = 5

# Các phương án nới lỏng mà agent được phép đề xuất, theo thứ tự ưu tiên:
# nới cái ít ảnh hưởng tới chất lượng ghép đôi trước.
RELAXATION_LADDER = (
    ("max_distance_km", "Mở rộng bán kính tìm kiếm"),
    ("age_min", "Hạ giới hạn tuổi dưới"),
    ("age_max", "Nâng giới hạn tuổi trên"),
    ("accepted_intents", "Chấp nhận thêm loại quan hệ khác"),
)


def compute_compatibility(user_id_a, user_id_b, store=None):
    """Chấm độ tương thích giữa hai người dùng cụ thể.

    Luôn chạy filter cứng trước: nếu cặp này bị chặn, trả về lý do thay vì
    một con số. Đưa ra điểm cho cặp đã bị chặn là sai về mặt sản phẩm —
    người dùng sẽ bám vào con số và bỏ qua lý do.
    """
    store = store if store is not None else profiles_mod.load_profiles()

    profile_a = profiles_mod.get_profile(store, user_id_a)
    profile_b = profiles_mod.get_profile(store, user_id_b)

    missing = [uid for uid, prof in ((user_id_a, profile_a), (user_id_b, profile_b))
               if prof is None]
    if missing:
        return {
            "status": "error",
            "message": f"Không tìm thấy hồ sơ: {', '.join(missing)}",
        }

    for profile in (profile_a, profile_b):
        errors = profiles_mod.validate_profile(profile)
        if errors:
            return {
                "status": "blocked",
                "message": f"Hồ sơ {profile['user_id']} không hợp lệ.",
                "reasons": errors,
            }

    passed, reasons = filters.hard_filters(profile_a, profile_b)
    if not passed:
        return {
            "status": "blocked",
            "user_id_a": user_id_a,
            "user_id_b": user_id_b,
            "message": "Cặp này không vượt qua bộ lọc bắt buộc.",
            "reasons": reasons,
        }

    result = scoring.compatibility(profile_a, profile_b)
    return {"status": "ok", **result}


def search_candidates(user_id, overrides=None, limit=DEFAULT_LIMIT, store=None):
    """Tìm và xếp hạng ứng viên phù hợp cho một người dùng.

    `overrides` nới lỏng tiêu chí của chính `user_id` (và chỉ của người này).
    Trả về status 'ok' kèm danh sách đã xếp hạng, hoặc 'empty' kèm gợi ý nới.
    """
    store = store if store is not None else profiles_mod.load_profiles()

    seeker = profiles_mod.get_profile(store, user_id)
    if seeker is None:
        return {"status": "error", "message": f"Không tìm thấy hồ sơ: {user_id}"}

    errors = profiles_mod.validate_profile(seeker)
    if errors:
        return {
            "status": "blocked",
            "message": f"Hồ sơ {user_id} không đủ điều kiện tìm kiếm.",
            "reasons": errors,
        }

    eligible = []
    rejected = []
    for candidate_id, candidate in store.items():
        if candidate_id == user_id:
            continue
        passed, reasons = filters.hard_filters(seeker, candidate, overrides)
        if passed:
            eligible.append(candidate)
        else:
            rejected.append((candidate_id, reasons))

    if not eligible:
        return {
            "status": "empty",
            "user_id": user_id,
            "message": "Không có ứng viên nào vượt qua bộ lọc hiện tại.",
            "applied_overrides": dict(overrides or {}),
            "relaxation_hints": suggest_relaxations(user_id, store=store),
            "sample_rejections": tuple(
                {"user_id": cid, "reason": reasons[0]} for cid, reasons in rejected[:3]
            ),
        }

    ranked = []
    for candidate in eligible:
        result = scoring.compatibility(seeker, candidate)
        ranked.append({
            **profiles_mod.summary_card(candidate),
            "score": result["score"],
            "band": result["band"],
            "asymmetry": result["asymmetry"],
            "top_reasons": tuple(
                item["note"] for item in result["breakdown"][:3] if item["verdict"] == "tot"
            ),
            "flags": result["flags"],
        })

    ranked.sort(key=lambda item: item["score"], reverse=True)

    return {
        "status": "ok",
        "user_id": user_id,
        "total_eligible": len(ranked),
        "applied_overrides": dict(overrides or {}),
        "candidates": tuple(ranked[:limit]),
    }


def suggest_relaxations(user_id, store=None):
    """Thử từng phương án nới lỏng, trả về phương án nào mở ra bao nhiêu ứng viên.

    Chỉ đề xuất phương án THỰC SỰ có kết quả — gợi ý "hãy mở rộng bán kính"
    trong khi mở rộng vẫn ra 0 người là lời khuyên vô nghĩa và làm agent lặp
    vô ích. Không bao giờ đề xuất nới `deal_breakers` hay tiêu chí an toàn.
    """
    store = store if store is not None else profiles_mod.load_profiles()
    seeker = profiles_mod.get_profile(store, user_id)
    if seeker is None:
        return ()

    prefs = seeker.get("preferences", {}) or {}
    hints = []

    for field, description in RELAXATION_LADDER:
        override = _build_override(field, prefs)
        if override is None:
            continue

        count = _count_eligible(seeker, store, override)
        if count > 0:
            hints.append({
                "field": field,
                "description": description,
                "override": override,
                "would_yield": count,
            })

    hints.sort(key=lambda item: item["would_yield"], reverse=True)
    return tuple(hints)


def _build_override(field, prefs):
    """Sinh một bước nới lỏng cụ thể cho từng trường."""
    if field == "max_distance_km":
        current = prefs.get("max_distance_km")
        if not isinstance(current, (int, float)):
            return None
        return {"max_distance_km": current * 3}

    if field == "age_min":
        current = prefs.get("age_min")
        if not isinstance(current, int):
            return None
        from .schema import MIN_AGE
        return {"age_min": max(MIN_AGE, current - 5)}

    if field == "age_max":
        current = prefs.get("age_max")
        if not isinstance(current, int):
            return None
        return {"age_max": current + 5}

    if field == "accepted_intents":
        current = prefs.get("accepted_intents")
        if not current:
            return None
        # Bỏ ràng buộc danh sách ý định, vẫn giữ ma trận chặn cứng bên dưới.
        return {"accepted_intents": None}

    return None


def _count_eligible(seeker, store, override):
    """Đếm số ứng viên qua được filter cứng khi áp một override."""
    count = 0
    for candidate_id, candidate in store.items():
        if candidate_id == seeker.get("user_id"):
            continue
        passed, _ = filters.hard_filters(seeker, candidate, override)
        if passed:
            count += 1
    return count
