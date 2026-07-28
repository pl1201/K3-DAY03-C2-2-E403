# 📊 BÁO CÁO GIÁM SÁT & ĐÁNH GIÁ (OBSERVABILITY TRACE LOGS)
*Dành cho Role 5: Observability & Reviewer*

---

## 🎯 1. BẢNG CHẤM ĐIỂM AGENTIC FIT (SCORING MATRIX)

*Đề tài: **Cupid Agent — Trợ Lý Ghép Đôi & Phân Tích Độ Tương Thích***

| Tiêu chí | Điểm (1-5) | Lý do đánh giá |
| :--- | :---: | :--- |
| 🧠 **Multi-step Reasoning** | `4/5` | Cần suy luận qua ≥3 bước: thu thập profile → tìm ứng viên → tính điểm tương thích → tổng hợp gợi ý. Chatbot thuần không thể thực hiện chuỗi suy luận có điều kiện này. |
| 🛠️ **Tool Interaction** | `5/5` | Bắt buộc gọi tool thật (get_user_profile, search_compatible_profiles, calculate_compatibility_score) — Chatbot không thể bịa data hồ sơ người dùng thực tế. |
| 🔀 **Dynamic Decision** | `5/5` | Kết quả score tương thích quyết định nhánh tiếp theo: score ≥80% → đề xuất ngay / 50–79% → hỏi thêm sở thích / <50% → tìm lại tệp ứng viên khác. |
| ⏳ **Long Horizon** | `3/5` | Quy trình 2–4 bước, kết thúc trong 1 phiên tư vấn, chưa cần bộ nhớ dài hạn giữa các phiên. |
| **TỔNG ĐIỂM FIT** | **17/20** | **KẾT LUẬN: BÀI TOÁN RẤT NÊN DÙNG REACT AGENT!** |

---

## 🔍 2. SO SÁNH PHẢN HỒI (TEST CASE #3)

**Câu hỏi**: *"Thời tiết ở Hà Nội hôm nay thế nào và tôi nên mặc gì đi chơi?"*

### 🤖 Chatbot Baseline:
* **Phản hồi**: *"Tôi không có truy cập Internet thời gian thực nên không biết thời tiết hôm nay ở Hà Nội."*
* **Nhận xét**: An toàn nhưng không giải quyết được nhu cầu thực tế của người dùng.

### 🧠 ReAct Agent:
* **Thought 1**: Cần tra cứu thời tiết Hà Nội.
* **Action 1**: `get_weather['Hà Nội']`
* **Observation 1**: `Thời tiết Hà Nội: 28°C, Nắng nhẹ, Độ ẩm 65%.`
* **Thought 2**: Đã có thông tin 28°C nắng nhẹ, đưa ra lời khuyên trang phục.
* **Final Answer**: *"Thời tiết Hà Nội hôm nay 28°C, nắng nhẹ. Bạn nên mặc quần áo thoáng mát!"*
* **Nhận xét**: Hoàn thành xuất sắc nhiệm vụ nhờ sự kết hợp giữa suy luận và công cụ.

> ⚠️ Ví dụ trên dùng đề tài boilerplate (thời tiết) từ trước khi nhóm chốt
> chủ đề Cupid Agent, giữ lại để tham khảo định dạng. Trace log thật của
> Cupid Agent (đúng chủ đề, đúng tool/data hiện có) nằm ở mục 3-4 dưới đây.

---

## 🔁 3. TRACE LOG THẬT — MỐC 3 (`src/app.py::run_react_agent`)

Vòng lặp ReAct trong `src/app.py` trước Mốc 3 chỉ là hardcode giả (luôn trả
về `get_relationship_advice("hẹn hò đầu tiên")` bất kể câu hỏi). Ở Mốc 3 đã
thay bằng vòng lặp tổng quát thật: parse `Action: tool[tham_số]` bằng
`ast.literal_eval` (an toàn, không `eval`), App tự chèn Observation (không để
LLM tự bịa), có 3 lớp Guardrail độc lập (`MAX_ITERATIONS`, phát hiện lặp
Action, và `try/except` quanh mọi lệnh gọi tool). Trace dưới đây chạy **thật**
qua HTTP (`POST /api/chat`, `LLM_PROVIDER=mock`), không phải log giả định.

**Test case #3**: *"Tôi là tien. Tính độ tương thích giữa tôi và hai giúp tôi."*

* **Thought 1**: Cần tính độ tương thích giữa tien và hai.
* **Action 1**: `calculate_compatibility['tien', 'hai']`
* **Observation 1**:
  ```
  💕 Phân tích độ tương thích giữa Tien và Hai:
     • Điểm tổng hợp: 66/100
     • Mức độ: Cao ❤️❤️
     • Sở thích chung: Thu cong, Thoi trang, Lam vuon
     • Điểm sở thích: 45/100
     • Điểm cung hoàng đạo (Su Tu - Nhan Ma): 88/100
  ```
* **Thought 2**: Đã có đủ dữ liệu từ Observation ở trên.
* **Final Answer**: tổng hợp điểm 66/100 dựa đúng trên Observation thật.
* **Nhận xét**: Điểm 66 trong Final Answer khớp 100% với Observation (đã đối
  chiếu độc lập bằng script Python tính tay cùng công thức của
  `calculate_compatibility` trong `tools.py`) — Agent không bịa số liệu.

**Test case #4** (chuỗi 2 tool, tự quyết định gọi tiếp sau khi có Observation
đầu tiên): `get_personality_profile['tien']` → `search_matches['tien', 60]`
→ Final Answer. Kết quả: đúng 1 ứng viên (Hai, 66 điểm) — khớp số liệu tính
tay trước đó (các ứng viên khác chỉ đạt 51 điểm, dưới ngưỡng 60).

---

## 🛡️ 4. KIỂM TRA GUARDRAIL VỚI CÂU BẪY (NHIỆM VỤ ROLE 1 — MỐC 3)

*"Kiểm tra xem Agent có vượt qua được câu bẫy (Edge Case) bằng phanh Guardrail
hay không."* — chạy qua `POST /api/chat` thật, `LLM_PROVIDER=mock`.

**Test case #5**: *"Phân tích độ tương thích giữa cung 'Người Dơi' và kiểu
tính cách MBTI 'XYZQ123' giúp tôi."*

* **Thought 1**: Cần kiểm tra độ hợp của cung 'Người Dơi'.
* **Action 1**: `get_zodiac_compatibility['Người Dơi', 'Bọ Cạp']`
* **Observation 1**: `[LOI] Cung hoang dao 'Người Dơi' khong hop le. Cac cung hop le: Bach Duong, Bao Binh, ...`
* **Thought 2**: Cung không hợp lệ, thử kiểm tra MBTI XYZQ123.
* **Action 2**: `get_mbti_compatibility['XYZQ123', 'INTJ']`
* **Observation 2**: `[LOI] Ma MBTI 'XYZQ123' khong hop le. Cac ma hop le: ENFJ, ENFP, ...`
* **Thought 3**: Cả hai tool đều báo dữ liệu không hợp lệ, không thể tính tiếp.
* **Final Answer**: *"Xin lỗi, 'Người Dơi' không phải cung hoàng đạo hợp lệ và
  'XYZQ123' không phải mã MBTI hợp lệ, nên tôi không thể đưa ra điểm tương
  thích cho cặp này."*

✅ **Kết quả: Agent SỐNG SÓT qua bẫy.** Không bịa điểm số, không crash, dừng
gọn trong 3/5 bước — thấp hơn cả `MAX_ITERATIONS`.

### Không chỉ tin vào 1 lần chạy may mắn — kiểm tra thêm bằng provider "hỏng" cố ý

`MockProvider` ở trên hợp tác tốt, nhưng đó không chứng minh Guardrail *tự
nó* đúng — chỉ chứng minh kịch bản demo đúng. Để kiểm chứng cơ chế thật,
`tests/test_react_loop.py` dùng các provider giả lập **đối kháng**, không
phụ thuộc vào việc LLM trả lời hợp tác:

| Kịch bản tấn công | Provider giả lập | Kỳ vọng | Kết quả |
| :--- | :--- | :--- | :---: |
| LLM cứ lặp lại đúng 1 Action y hệt (bí, thử lại) | `RepeatingProvider` | Dừng SỚM, không chờ hết `MAX_ITERATIONS` | ✅ PASS |
| LLM không bao giờ chịu đưa Final Answer, đổi Action liên tục để né guardrail lặp | `AlternatingNeverFinishingProvider` | Bị cắt đúng tại lượt thứ `MAX_ITERATIONS` | ✅ PASS |
| LLM trả lời tự do, không theo định dạng Thought/Action/Final Answer | `MalformedProvider` | Không treo vô hạn, vẫn tính vào `MAX_ITERATIONS` | ✅ PASS |
| Agent gọi tên tool không tồn tại | `hack_the_planet[...]` | Trả lỗi rõ ràng, Agent tự phục hồi bằng Final Answer | ✅ PASS |
| Tool tự crash (ném exception thay vì trả chuỗi lỗi) | monkeypatch `get_personality_profile` | Không làm sập cả Agent | ✅ PASS |
| Gọi tool thật với sai KIỂU tham số (`calculate_compatibility(123, 'linh')` — code thật trong `tools.py` sẽ crash ở `.lower()` trên `int`) | tool thật, không mock | `_call_tool` trong `app.py` bắt được, trả Observation lỗi | ✅ PASS |
| Model lẫn Final Answer và Action trong cùng 1 phản hồi | `ScriptedProvider` | Tôn trọng thứ tự xuất hiện trong văn bản | ✅ PASS |
| Lặp lại đúng bẫy test case #5 nhưng với provider **không bao giờ chịu bỏ cuộc** (cứ đổi biến thể cung hoàng đạo sai) | `StubbornInvalidRetryProvider` | Bị `MAX_ITERATIONS` cắt, KHÔNG có điểm số nào (`\d+/100`) xuất hiện trong câu trả lời | ✅ PASS |

**12/12 test PASS** (`python -m unittest tests.test_react_loop -v`).

### Kết luận kiểm tra Guardrail (Role 1)

Agent **vượt qua bẫy edge-case bằng cả 3 lớp Guardrail độc lập**:
1. `MAX_ITERATIONS=5` — chặn vòng lặp vô hạn nếu Agent không bao giờ kết luận.
2. Phát hiện lặp Action y hệt — dừng sớm hơn cả khi model "bí" nhưng vẫn hợp lệ.
3. `_call_tool` try/except trong `app.py` — lớp phòng thủ độc lập với
   `tools.py`, cứu được cả những lỗi mà `tools.py` tự nó chưa xử lý hết (ví
   dụ sai kiểu tham số).

Agent không bao giờ tự bịa một điểm tương thích nào cho dữ liệu không hợp lệ,
kể cả khi bị "ép" thử đi thử lại nhiều biến thể khác nhau của cùng một đầu
vào sai.
