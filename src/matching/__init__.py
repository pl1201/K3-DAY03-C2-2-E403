"""Engine ghép đôi & phân tích độ tương thích cho Cupid Agent.

API công khai dành cho Role 2 (Tool Engineer) — bọc các hàm này thành Tool:

    from matching import search_candidates, compute_compatibility
    from matching import format_search, format_compatibility

    def find_matches(user_id: str) -> str:
        '''Tìm ứng viên phù hợp cho một người dùng.'''
        return format_search(search_candidates(user_id))

Kiến trúc 3 tầng (xem docs/PRODUCT_DESIGN_CUPID.md):
    Tầng 0  filters.safety_gate      — điều kiện an toàn, nhị phân
    Tầng 1  filters.hard_filters     — lọc cứng HAI CHIỀU
    Tầng 2  scoring.compatibility    — điểm mềm, trung bình nhân hai chiều

Engine hoàn toàn tất định và không gọi LLM: cùng đầu vào luôn cho cùng đầu ra,
và nội dung do người dùng nhập (bio, sở thích) không bao giờ được diễn giải
như chỉ thị.
"""

from .engine import compute_compatibility, search_candidates, suggest_relaxations
from .profiles import (
    get_profile,
    load_profiles,
    public_view,
    summary_card,
    validate_profile,
)
from .report import (
    format_compatibility,
    format_profile,
    format_search,
)

__all__ = [
    # Điều phối
    "search_candidates",
    "compute_compatibility",
    "suggest_relaxations",
    # Dữ liệu
    "load_profiles",
    "get_profile",
    "public_view",
    "summary_card",
    "validate_profile",
    # Trình bày
    "format_search",
    "format_compatibility",
    "format_profile",
]
