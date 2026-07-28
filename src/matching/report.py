"""Chuyển kết quả engine thành văn bản tiếng Việt cho Agent/người dùng đọc.

Tách khỏi `engine.py` để logic tính toán không dính tới cách trình bày.
Role 2 có thể gọi thẳng các hàm ở đây làm giá trị trả về của Tool.

Nguyên tắc trình bày: LUÔN kèm phân rã theo trục, không bao giờ chỉ trả về
một con số trần. Người dùng cần biết điểm đến từ đâu để tự phán đoán.
"""

VERDICT_ICON = {"tot": "✓", "kha": "△", "luu_y": "✗"}


def format_compatibility(result):
    """Định dạng đầu ra của `engine.compute_compatibility`."""
    status = result.get("status")

    if status == "error":
        return f"LỖI: {result.get('message')}"

    if status == "blocked":
        lines = [f"KHÔNG THỂ GHÉP ĐÔI: {result.get('message')}"]
        lines.extend(f"  - {reason}" for reason in result.get("reasons", ()))
        lines.append(
            "Đây là kết quả của bộ lọc bắt buộc, không phải điểm số thấp — "
            "không có con số tương thích nào được đưa ra cho cặp này."
        )
        return "\n".join(lines)

    lines = [
        f"ĐỘ TƯƠNG THÍCH {result['user_id_a']} ↔ {result['user_id_b']}: "
        f"{result['score']}/100 — {result['band']}",
        f"  Chiều {result['user_id_a']}→{result['user_id_b']}: {result['score_a_to_b']} | "
        f"chiều ngược lại: {result['score_b_to_a']} "
        f"(lệch {result['asymmetry']} điểm)",
        "",
        "PHÂN RÃ THEO TRỤC:",
    ]

    for item in result.get("breakdown", ()):
        icon = VERDICT_ICON.get(item["verdict"], "-")
        lines.append(
            f"  {icon} {item['label']:<12} {item['score']:>3}/100  "
            f"(trọng số {item['weight']})  {item['note']}"
        )

    flags = result.get("flags", ())
    if flags:
        lines.append("")
        lines.append("CẦN LƯU Ý:")
        lines.extend(f"  ⚠ {flag}" for flag in flags)

    starters = result.get("conversation_starters", ())
    if starters:
        lines.append("")
        lines.append("GỢI Ý MỞ LỜI:")
        lines.extend(f"  💬 {item}" for item in starters)

    return "\n".join(lines)


def format_search(result):
    """Định dạng đầu ra của `engine.search_candidates`."""
    status = result.get("status")

    if status == "error":
        return f"LỖI: {result.get('message')}"

    if status == "blocked":
        lines = [f"KHÔNG THỂ TÌM KIẾM: {result.get('message')}"]
        lines.extend(f"  - {reason}" for reason in result.get("reasons", ()))
        return "\n".join(lines)

    if status == "empty":
        return _format_empty(result)

    lines = [
        f"TÌM THẤY {result['total_eligible']} ứng viên phù hợp cho "
        f"{result['user_id']} (hiển thị {len(result['candidates'])} người tốt nhất):"
    ]

    overrides = result.get("applied_overrides")
    if overrides:
        lines.append(f"  [Đã nới lỏng tiêu chí: {overrides}]")

    for index, candidate in enumerate(result["candidates"], start=1):
        lines.append(
            f"  {index}. {candidate['user_id']} — {candidate['display_name']}, "
            f"{candidate['age']} tuổi, {candidate.get('district') or ''} "
            f"{candidate.get('city') or ''} | {candidate.get('occupation') or ''}"
        )
        lines.append(f"     Điểm: {candidate['score']}/100 ({candidate['band']})")
        for reason in candidate.get("top_reasons", ()):
            lines.append(f"     ✓ {reason}")
        for flag in candidate.get("flags", ()):
            lines.append(f"     ⚠ {flag}")

    return "\n".join(lines)


def _format_empty(result):
    """Trường hợp 0 kết quả — phải nêu rõ phương án tiếp theo, không bỏ lửng.

    Đây là thông điệp điều khiển vòng lặp ReAct: agent đọc `relaxation_hints`
    rồi tự quyết định gọi lại `search_candidates` với override nào.
    """
    lines = [
        f"KHÔNG CÓ ỨNG VIÊN NÀO cho {result['user_id']} với tiêu chí hiện tại."
    ]

    overrides = result.get("applied_overrides")
    if overrides:
        lines.append(f"  (đã áp dụng nới lỏng: {overrides})")

    samples = result.get("sample_rejections", ())
    if samples:
        lines.append("  Ví dụ lý do bị loại:")
        lines.extend(f"    - {item['user_id']}: {item['reason']}" for item in samples)

    hints = result.get("relaxation_hints", ())
    if hints:
        lines.append("")
        lines.append("  PHƯƠNG ÁN NỚI LỎNG KHẢ THI (chọn 1 rồi gọi lại tool):")
        for hint in hints:
            lines.append(
                f"    - {hint['description']}: override={hint['override']} "
                f"→ mở ra {hint['would_yield']} ứng viên"
            )
    else:
        lines.append("")
        lines.append(
            "  Không có phương án nới lỏng nào tạo ra kết quả. Hãy dừng tìm kiếm "
            "và trao đổi lại với người dùng thay vì thử tiếp."
        )

    return "\n".join(lines)


def format_profile(profile):
    """Hiển thị hồ sơ đã qua `profiles.public_view` — không có dữ liệu riêng tư."""
    from . import schema

    location = profile.get("location", {})
    socio = profile.get("socio", {})
    psycho = profile.get("psycho", {})

    lines = [
        f"HỒ SƠ {profile.get('user_id')} — {profile.get('display_name')}",
        f"  Tuổi: {profile.get('age')} | "
        f"Giới tính: {schema.label(profile.get('gender'))} | "
        f"Ý định: {schema.label(profile.get('intent'))}",
        f"  Nơi ở: {location.get('district', '')} {location.get('city', '')}",
        f"  Học vấn: {schema.label(socio.get('education'))} | "
        f"Nghề nghiệp: {socio.get('occupation', '?')}",
    ]

    interests = psycho.get("interests")
    if interests:
        lines.append(f"  Sở thích: {', '.join(interests)}")

    return "\n".join(lines)
