# 💕 CUPID AGENT - TÓM TẮT DỰ ÁN

**Chủ đề**: Trợ Lý Ghép Đôi & Phân Tích Độ Tương Thích  
**Lab**: Chatbot vs ReAct Agent (Day 3)  
**Ngày cập nhật**: 2026-07-28

---

## 🎯 TỔNG QUAN DỰ ÁN

Cupid Agent là một hệ thống AI thông minh giúp:
- 📋 Tra cứu hồ sơ tính cách và sở thích người dùng
- 💕 Tính toán độ tương thích giữa hai người
- 🔍 Tìm kiếm đối tượng phù hợp dựa trên thuật toán matching
- 💡 Đưa ra lời khuyên về mối quan hệ

---

## 🛠️ 4 TOOLS CHÍNH

| Tool | Chức năng | Input | Output |
|:-----|:----------|:------|:-------|
| `get_personality_profile` | Lấy hồ sơ người dùng | user_id | Tuổi, tính cách, sở thích, cung hoàng đạo |
| `calculate_compatibility` | Tính độ tương thích | user1_id, user2_id | Điểm 0-100, phân tích chi tiết |
| `search_matches` | Tìm đối tượng phù hợp | user_id, min_score | Danh sách người phù hợp |
| `get_relationship_advice` | Lời khuyên mối quan hệ | situation | 5 lời khuyên cụ thể |

---

## 👥 DATABASE MẪU

| User | Tuổi | Tính cách | Sở thích | Cung |
|:-----|:----:|:----------|:---------|:-----|
| **Minh** | 25 | Hướng ngoại, Năng động | Du lịch, Thể thao, Âm nhạc, Nấu ăn | Bạch Dương |
| **Linh** | 24 | Hướng ngoại, Hoạt bát | Du lịch, Âm nhạc, Đọc sách, Yoga | Sư Tử |
| **Huy** | 27 | Hướng nội, Tư duy logic | Đọc sách, Lập trình, Cờ vua, Phim | Xử Nữ |
| **Nga** | 23 | Hướng nội, Nhạy cảm | Hội họa, Âm nhạc, Đọc sách, Cà phê | Song Ngư |
| **Tuấn** | 26 | Hướng ngoại, Hài hước | Thể thao, Du lịch, Game, Ẩm thực | Nhân Mã |

---

## 🧪 6 TEST CASES

### 🟢 Case 1-2: Đơn giản (Chỉ cần LLM)
- Lời khuyên hẹn hò đầu tiên
- Phân biệt tính cách hướng ngoại/nội

**Kỳ vọng**: Chatbot baseline có thể trả lời tốt

---

### 🟡 Case 3: Multi-step (Cần 2 Tools)
**Câu hỏi**: "Cho tôi biết hồ sơ của Minh và cho lời khuyên hẹn hò đầu tiên cho bạn ấy."

**Agent Flow**:
1. **Thought**: Cần tra cứu hồ sơ Minh
2. **Action**: `get_personality_profile('minh')`
3. **Observation**: Minh 25 tuổi, hướng ngoại, thích du lịch...
4. **Thought**: Cần lời khuyên hẹn hò
5. **Action**: `get_relationship_advice('hẹn hò đầu tiên')`
6. **Observation**: 5 lời khuyên chi tiết
7. **Final Answer**: Tổng hợp cá nhân hóa dựa trên tính cách Minh

---

### 🟡 Case 4: Phức tạp (Cần 2-3 Tools)
**Câu hỏi**: "Tính độ tương thích giữa Minh và Linh, sau đó tìm tất cả người phù hợp với Minh."

**Agent Flow**:
1. `calculate_compatibility('minh', 'linh')` → 60/100
2. `search_matches('minh', 60)` → Linh, Tuấn
3. Tổng hợp kết quả

---

### 🔴 Case 5: Edge Case (Bẫy Guardrail)
**Câu hỏi**: "Tính độ tương thích giữa người dùng XYZ123 và ABC999 không tồn tại."

**Kỳ vọng**:
- Tool trả về lỗi: "Không tìm thấy user XYZ123"
- Agent nhận ra và dừng lại
- Guardrail ngắt an toàn, không lặp vô hạn
- Thông báo lịch sự cho user

---

### 🟡 Case 6: Kịch bản thực tế
**Câu hỏi**: "Tôi là Huy, hãy tìm người phù hợp nhất với tôi và phân tích tại sao."

**Agent Flow**:
1. `search_matches('huy', 60)` → Danh sách candidates
2. `calculate_compatibility('huy', candidate)` cho từng người
3. Phân tích chi tiết lý do phù hợp

---

## 📊 AGENTIC FIT SCORE: 19/20

| Tiêu chí | Điểm | Lý do |
|:---------|:----:|:------|
| 🧠 Multi-step Reasoning | 5/5 | Cần nhiều bước suy luận liên tiếp |
| 🛠️ Tool Interaction | 5/5 | 4 tools có thể kết hợp linh hoạt |
| 🔀 Dynamic Decision | 5/5 | Kết quả bước trước ảnh hưởng bước sau |
| ⏳ Long Horizon | 4/5 | 3-4 bước, có thể mở rộng với memory |

**Kết luận**: ✅ **Rất phù hợp với ReAct Agent!** Không nên dùng Chatbot thuần vì sẽ bịa thông tin về người dùng.

---

## 🎭 SO SÁNH CHATBOT VS AGENT

### Chatbot Baseline ❌
```
User: "Cho tôi biết hồ sơ của Minh"
Bot: "Tôi không có thông tin cụ thể về Minh trong hệ thống..."
```
- ❌ Không có grounding
- ❌ Không tra cứu database
- ✅ Trả lời an toàn nhưng vô dụng

### ReAct Agent ✅
```
Thought: Cần tra cứu hồ sơ Minh
Action: get_personality_profile('minh')
Observation: Minh 25 tuổi, hướng ngoại...
Final Answer: "Minh là người 25 tuổi, tính cách hướng ngoại..."
```
- ✅ Có grounding từ database
- ✅ Dữ liệu chính xác
- ✅ Cá nhân hóa dựa trên thông tin thực

---

## 🔄 CÁCH CHẠY DEMO

```bash
# 1. Cài đặt môi trường
cd K3-Day03-Lab-Chatbot-vs-react-agent-E403
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Chạy app
python src/app.py

# 3. Output sẽ hiển thị:
# - Demo Chatbot Baseline
# - Demo ReAct Agent với Thought-Action-Observation
# - Test từng tool độc lập
# - Test edge case
```

---

## 📁 CẤU TRÚC FILES

```
📁 K3-Day03-Lab-Chatbot-vs-react-agent-E403/
├── 📁 config/
│   └── test_cases.json          ✅ 6 test cases cho Cupid Agent
├── 📁 src/
│   ├── tools.py                 ✅ 4 tools + database
│   ├── prompts.py               ✅ System prompts cho Cupid Agent
│   ├── app.py                   ✅ Demo app với ReAct loop
│   └── providers.py             (Mock provider cho offline testing)
└── 📁 docs/
    ├── trace_eval.md            ✅ Báo cáo chi tiết Agentic Fit
    ├── ROLE2_COMPLETION_REPORT.md ✅ Báo cáo hoàn thành Role 2
    └── CUPID_AGENT_SUMMARY.md   📄 File này
```

---

## 🎓 BÀI HỌC QUAN TRỌNG

### 1. Khi nào KHÔNG nên dùng Agent?
- ❌ Câu hỏi lý thuyết đơn giản
- ❌ Không cần dữ liệu thời gian thực
- ❌ Tốc độ quan trọng hơn độ chính xác

### 2. Khi nào NÊN dùng Agent?
- ✅ Cần tra cứu database/API
- ✅ Multi-step reasoning
- ✅ Độ chính xác > Tốc độ
- ✅ Không được phép bịa thông tin

### 3. Trade-offs
| Yếu tố | Chatbot | Agent |
|:-------|:-------:|:-----:|
| Tốc độ | ⚡⚡⚡ | ⚡ |
| Chi phí | 💰 | 💰💰💰 |
| Độ chính xác | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Grounding | ❌ | ✅ |

---

## 🚀 BƯỚC TIẾP THEO

### Cho Role 3 (Prompt Engineer):
- [ ] Tinh chỉnh REACT_SYSTEM_PROMPT
- [ ] Thêm few-shot examples
- [ ] Cấu hình Guardrails chi tiết hơn

### Cho Role 4 (Integrator):
- [ ] Implement parser thật cho Thought-Action-Observation
- [ ] Tích hợp LLM thật (OpenAI/Anthropic/Gemini)
- [ ] Xử lý error handling toàn diện

### Cho Role 5 (Observability):
- [ ] Thu thập trace logs từ LLM thực tế
- [ ] Vẽ Hybrid Flowchart (Chatbot vs Agent decision)
- [ ] So sánh chi phí token thực tế

### Bonus - Autonomous Agent (Cấp 4):
- [ ] Thêm Planning: Tự chia nhỏ mục tiêu
- [ ] Thêm Memory: Nhớ lịch sử tương tác
- [ ] Self-evaluation: Tự đánh giá kết quả

---

## 🎉 THÀNH TÍCH

- ✅ Thiết kế 4 tools hoàn chỉnh
- ✅ Database deterministic với 5 users
- ✅ 6 test cases đa dạng (đơn giản → phức tạp → edge case)
- ✅ Agentic Fit Score: 19/20
- ✅ Demo app chạy thành công
- ✅ Tài liệu chi tiết đầy đủ

**Cupid Agent đã sẵn sàng để các roles khác tích hợp!** 💕🚀
