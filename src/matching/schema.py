"""Lược đồ dữ liệu & bảng tra tĩnh cho engine ghép đôi Cupid Agent.

Module này CHỈ chứa dữ liệu tĩnh (tập giá trị hợp lệ, bảng tra, thang đo,
trọng số mặc định). Toàn bộ logic nằm ở `filters.py` và `scoring.py`.

Quy ước: giá trị lưu trong hồ sơ dùng slug ASCII không dấu (vd "xa_giao")
để tránh lỗi mã hoá khi đưa vào prompt/JSON. Nhãn tiếng Việt có dấu để
hiển thị cho người dùng nằm ở `LABELS`.
"""

# --- Cổng an toàn -----------------------------------------------------------

MIN_AGE = 18

# --- Định danh & xu hướng ---------------------------------------------------

GENDERS = ("nam", "nu", "phi_nhi_nguyen")

ORIENTATIONS = (
    "di_tinh",      # dị tính
    "dong_tinh",    # đồng tính
    "song_tinh",    # song tính
    "toan_tinh",    # toàn tính
    "vo_tinh",      # vô tính
)

RELATIONSHIP_STATUS = (
    "doc_than",
    "dang_hen_ho",
    "da_ket_hon",
    "ly_than",
    "mo",           # mối quan hệ mở
)

# Tình trạng hôn nhân xung đột với ý định tìm mối quan hệ độc quyền.
EXCLUSIVE_INTENTS = ("ban_doi", "nghiem_tuc")
COMMITTED_STATUS = ("dang_hen_ho", "da_ket_hon")

# --- Ý định quan hệ ---------------------------------------------------------

INTENTS = (
    "ban_doi",          # tìm bạn đời
    "nghiem_tuc",       # hẹn hò nghiêm túc
    "nhe_nhang",        # hẹn hò nhẹ nhàng
    "ban_be",           # kết bạn
    "khong_rang_buoc",  # không ràng buộc
)

# Ma trận tương thích ý định (0-100). Ô 0 = CHẶN CỨNG, không phải điểm thấp:
# "tìm bạn đời" và "không ràng buộc" là mâu thuẫn nền tảng, ghép đôi hai
# người này gây tổn thương thật chứ không chỉ là một gợi ý kém.
INTENT_MATRIX = {
    "ban_doi":         {"ban_doi": 100, "nghiem_tuc": 80,  "nhe_nhang": 30,  "ban_be": 20,  "khong_rang_buoc": 0},
    "nghiem_tuc":      {"ban_doi": 80,  "nghiem_tuc": 100, "nhe_nhang": 60,  "ban_be": 30,  "khong_rang_buoc": 10},
    "nhe_nhang":       {"ban_doi": 30,  "nghiem_tuc": 60,  "nhe_nhang": 100, "ban_be": 50,  "khong_rang_buoc": 60},
    "ban_be":          {"ban_doi": 20,  "nghiem_tuc": 30,  "nhe_nhang": 50,  "ban_be": 100, "khong_rang_buoc": 30},
    "khong_rang_buoc": {"ban_doi": 0,   "nghiem_tuc": 10,  "nhe_nhang": 60,  "ban_be": 30,  "khong_rang_buoc": 100},
}

# --- Lối sống (thang thứ bậc) ----------------------------------------------

DRINK_SCALE = {"khong": 0, "hiem_khi": 1, "xa_giao": 2, "thuong_xuyen": 3, "nhieu": 4}
SMOKE_SCALE = {"khong": 0, "dang_cai": 1, "thinh_thoang": 2, "thuong_xuyen": 3}
DRUG_SCALE = {"khong": 0, "thinh_thoang": 1, "thuong_xuyen": 2}
EXERCISE_SCALE = {"khong": 0, "thinh_thoang": 1, "thuong_xuyen": 2, "hang_ngay": 3}
SLEEP_SCALE = {"day_som": 0, "linh_hoat": 1, "cu_dem": 2}

# Các trường lối sống mà điểm số đến từ PREFERENCE của người chấm,
# không phải từ độ giống nhau giữa hai giá trị. Xem `scoring.score_lifestyle`.
PREFERENCE_DRIVEN_LIFESTYLE = ("drinks", "smokes", "drugs")

# Các trường lối sống chấm theo độ tương đồng thứ bậc.
SIMILARITY_LIFESTYLE = {
    "exercise": EXERCISE_SCALE,
    "sleep": SLEEP_SCALE,
}

# --- Học vấn ----------------------------------------------------------------

EDUCATION_RANK = {
    "thpt": 1,
    "cao_dang": 2,
    "dai_hoc": 3,
    "thac_si": 4,
    "tien_si": 5,
}

# --- Gia đình ---------------------------------------------------------------

CHILD_PLANS = ("muon", "khong_muon", "chua_xac_dinh")

# --- Tâm lý -----------------------------------------------------------------

BIG_FIVE_TRAITS = ("openness", "conscientiousness", "extraversion",
                   "agreeableness", "neuroticism")

MBTI_LETTERS = (("E", "I"), ("N", "S"), ("T", "F"), ("J", "P"))

# Trọng số heuristic cho từng cặp chữ cái MBTI.
# LƯU Ý KHOA HỌC: MBTI có độ tin cậy test-retest thấp và không được xem là
# công cụ dự báo kết quả quan hệ. Ở đây dùng như một tín hiệu "vui" có
# trọng số thấp, KHÔNG phải trục quyết định. Big Five đáng tin hơn.
MBTI_RULES = (
    # (chỉ số cặp chữ, điểm nếu GIỐNG, điểm nếu KHÁC)
    (0, 0.10, 0.25),   # E/I  -> bù trừ thường tốt hơn
    (1, 0.35, 0.05),   # N/S  -> cùng cách tiếp nhận thông tin là tín hiệu mạnh nhất
    (2, 0.25, 0.15),   # T/F
    (3, 0.10, 0.15),   # J/P  -> bù trừ nhẹ
)

ZODIAC_ELEMENT = {
    "bach_duong": "lua", "su_tu": "lua", "nhan_ma": "lua",
    "kim_nguu": "dat", "xu_nu": "dat", "ma_ket": "dat",
    "song_tu": "khi", "thien_binh": "khi", "bao_binh": "khi",
    "cu_giai": "nuoc", "bo_cap": "nuoc", "song_ngu": "nuoc",
}

# Nguyên tố hợp nhau theo chiêm tinh phương Tây cổ điển.
ELEMENT_AFFINITY = {
    ("lua", "lua"): 0.85, ("lua", "khi"): 0.90, ("lua", "dat"): 0.45, ("lua", "nuoc"): 0.35,
    ("dat", "dat"): 0.85, ("dat", "nuoc"): 0.90, ("dat", "khi"): 0.40,
    ("khi", "khi"): 0.85, ("khi", "nuoc"): 0.45,
    ("nuoc", "nuoc"): 0.85,
}

# --- Trọng số mặc định ------------------------------------------------------

# Người dùng có thể ghi đè qua profile["weights"]. Thang: 0 = không quan tâm,
# 10 = cực kỳ quan trọng. Giá trị "MANDATORY" được xử lý ở deal_breakers
# (filter cứng), không nằm trong thang trọng số này.
DEFAULT_WEIGHTS = {
    "intent": 10,
    "distance": 6,
    "lifestyle": 8,
    "education": 3,
    "career": 2,
    "personality": 5,
    "interests": 4,
    "family": 6,
}

SCORING_DIMENSIONS = tuple(DEFAULT_WEIGHTS.keys())

# Khoảng cách: điểm giảm dần từ 1.0 (rất gần) xuống DISTANCE_FLOOR khi chạm
# bán kính tối đa. Không giảm về 0 vì cặp đã qua được filter khoảng cách.
DISTANCE_NEAR_KM = 5.0
DISTANCE_FLOOR = 0.30

# Ngưỡng diễn giải điểm tổng.
SCORE_BANDS = (
    (85, "Rất tiềm năng"),
    (70, "Tiềm năng"),
    (55, "Trung bình"),
    (40, "Thấp"),
    (0, "Rất thấp"),
)

# --- Nhãn hiển thị tiếng Việt ----------------------------------------------

LABELS = {
    "nam": "Nam", "nu": "Nữ", "phi_nhi_nguyen": "Phi nhị nguyên",
    "di_tinh": "Dị tính", "dong_tinh": "Đồng tính", "song_tinh": "Song tính",
    "toan_tinh": "Toàn tính", "vo_tinh": "Vô tính",
    "doc_than": "Độc thân", "dang_hen_ho": "Đang hẹn hò",
    "da_ket_hon": "Đã kết hôn", "ly_than": "Ly thân", "mo": "Mối quan hệ mở",
    "ban_doi": "Tìm bạn đời", "nghiem_tuc": "Hẹn hò nghiêm túc",
    "nhe_nhang": "Hẹn hò nhẹ nhàng", "ban_be": "Kết bạn",
    "khong_rang_buoc": "Không ràng buộc",
    "khong": "Không", "hiem_khi": "Hiếm khi", "xa_giao": "Xã giao",
    "thuong_xuyen": "Thường xuyên", "nhieu": "Nhiều",
    "dang_cai": "Đang cai", "thinh_thoang": "Thỉnh thoảng",
    "hang_ngay": "Hàng ngày",
    "day_som": "Dậy sớm", "linh_hoat": "Linh hoạt", "cu_dem": "Cú đêm",
    "thpt": "THPT", "cao_dang": "Cao đẳng", "dai_hoc": "Đại học",
    "thac_si": "Thạc sĩ", "tien_si": "Tiến sĩ",
    "muon": "Muốn có con", "khong_muon": "Không muốn có con",
    "chua_xac_dinh": "Chưa xác định",
    "intent": "Ý định", "distance": "Khoảng cách", "lifestyle": "Lối sống",
    "education": "Học vấn", "career": "Nghề nghiệp",
    "personality": "Tính cách", "interests": "Sở thích", "family": "Gia đình",
}


def label(slug):
    """Trả về nhãn tiếng Việt của một slug, fallback về chính slug."""
    return LABELS.get(slug, slug)
