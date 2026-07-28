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

## 📋 2. LOG CHATBOT BASELINE — MỐC 2 (5 TEST CASES)

### TC#1 — 🟢 Đơn giản (Chỉ cần LLM)
**Câu hỏi**: *"Làm sao để biết mình và đối phương thực sự hợp nhau, hay chỉ đang ở giai đoạn say nắng ban đầu?"*

**Phản hồi Chatbot** (nguyên văn):

> Để phân biệt giữa việc thực sự hợp nhau và chỉ đang ở giai đoạn say nắng ban đầu, bạn có thể xem xét một số dấu hiệu sau:
>
> 1. **Hiểu biết và Chấp nhận:** Nếu cả hai bên sẵn lòng chấp nhận và tôn trọng ưu điểm và khuyết điểm của nhau, đó là dấu hiệu tốt của sự hòa hợp. Tình cảm lâu bền thường vượt qua được những khó khăn thường ngày.
>
> 2. **Giao tiếp:** Khả năng trò chuyện cởi mở và trung thực về mọi thứ, từ những điều nhỏ nhặt đến những vấn đề lớn, là một yếu tố quan trọng. Nếu bạn cảm thấy hoàn toàn thoải mái khi nói chuyện với đối phương về bất cứ điều gì, đó có thể là dấu hiệu cho thấy sự kết nối mạnh mẽ.
>
> 3. **Giá trị và Mục tiêu:** Kiểm tra xem cả hai có những giá trị và mục tiêu sống tương tự hay không. Điều này không có nghĩa là mọi thứ phải hoàn toàn giống nhau, nhưng có sự tương đồng trong cách nhìn nhận những điều quan trọng có thể giúp mối quan hệ bền vững hơn.
>
> 4. **Cảm giác về tương lai:** Khi nghĩ về tương lai, bạn có thấy đối phương là một phần trong bản kế hoạch của mình không? Nếu cả hai đều cảm thấy như vậy và muốn cùng nhau trải qua những chương mới của cuộc đời, đó có thể là dấu hiệu của một mối quan hệ tiềm năng lâu dài.
>
> 5. **Xử lý mâu thuẫn:** Cách các bạn xử lý sự bất đồng cũng là một yếu tố quan trọng. Một cặp đôi hòa hợp thường có thể giải quyết mâu thuẫn một cách lành mạnh và học hỏi từ những cuộc tranh luận.
>
> Nếu bạn nhận thấy rằng phần lớn những điều trên đều tích cực, có khả năng mối quan hệ của bạn không chỉ dừng lại ở giai đoạn say nắng ban đầu. Tuy nhiên, thời gian sẽ là thước đo chính xác nhất để xem xét sự phát triển của một mối quan hệ. Hãy kiên nhẫn và cho cả hai thời gian để thực sự hiểu rõ về nhau.

**Phân loại**: ✅ **correct** — Trả lời đúng từ kiến thức có sẵn, không cần tool, không bịa dữ liệu cụ thể. tool_calls = 0.

---

### TC#2 — 🟢 Đơn giản (Chỉ cần LLM)
**Câu hỏi**: *"MBTI là gì và nó thường được dùng thế nào để tìm hiểu tính cách của một người?"*

**Phản hồi Chatbot** (nguyên văn):

> MBTI, viết tắt của Myers-Briggs Type Indicator, là một công cụ đánh giá tâm lý được phát triển dựa trên lý thuyết phân loại tính cách của Carl Jung. MBTI phân loại con người thành 16 kiểu tính cách khác nhau, dựa trên bốn cặp tiêu chí:
>
> 1. **Hướng ngoại (Extraversion - E) vs. Hướng nội (Introversion - I):** Điều này thể hiện cách bạn tương tác với thế giới xung quanh, bạn có xu hướng thu năng lượng từ người khác (hướng ngoại) hay từ bản thân (hướng nội).
>
> 2. **Giác quan (Sensing - S) vs. Trực giác (Intuition - N):** Cách bạn thu thập và xử lý thông tin. Bạn có thiên hướng quan tâm đến các chi tiết và thực tế (giác quan) hay bạn chú trọng vào bức tranh tổng thể và các khả năng tương lai (trực giác).
>
> 3. **Lý trí (Thinking - T) vs. Cảm xúc (Feeling - F):** Cách bạn đưa ra quyết định, dựa trên lý luận logic và khách quan (lý trí) hoặc trên cơ sở giá trị cá nhân và cảm xúc (cảm xúc).
>
> 4. **Nguyên tắc (Judging - J) vs. Linh hoạt (Perceiving - P):** Phong cách sống của bạn, có kế hoạch và tổ chức (nguyên tắc) hay tự phát và linh hoạt (linh hoạt).
>
> MBTI thường được sử dụng trong nhiều lĩnh vực như tuyển dụng, tư vấn nghề nghiệp, cải thiện giao tiếp nhóm, và phát triển cá nhân. Nó giúp mọi người hiểu hơn về bản thân, từ đó cải thiện quan hệ với người khác bằng cách nhận thức và tôn trọng sự khác biệt trong tính cách. Mặc dù MBTI là công cụ phổ biến để tìm hiểu và phát triển cá nhân, cần nhớ rằng đây không phải là một lý thuyết khoa học chính xác mà chỉ là một công cụ tự đánh giá hữu ích.

**Phân loại**: ✅ **correct** — Điểm cộng: Chatbot chủ động nêu giới hạn khoa học của MBTI mà không cần hỏi. tool_calls = 0.

---

### TC#3 — 🟡 Multi-step (Cần 1 Tool)
**Câu hỏi**: *"Tôi là tien. Tính độ tương thích giữa tôi và hai giúp tôi."*

**Phản hồi Chatbot** (nguyên văn):

> Xin chào Tiến! Mặc dù tôi không có thông tin cụ thể về bạn và đối tác của bạn, tôi có thể giúp bạn tìm hiểu về độ tương thích trong mối quan hệ bằng cách xem xét một số yếu tố quan trọng. Dưới đây là một số tiêu chí giúp bạn đánh giá:
>
> 1. **Giao tiếp**: Khả năng lắng nghe và thấu hiểu nhau quan trọng để giải quyết mọi xung đột và hiểu rõ nhu cầu, mong muốn của đối phương.
>
> 2. **Giá trị và Mục tiêu sống**: Sự tương thích trong các giá trị đạo đức, tôn giáo, và mục tiêu trong đời sống sẽ giúp cả hai hướng tới cùng một hướng dài hạn.
>
> 3. **Sở thích chung và Đam mê**: Có một số sở thích chung giúp gia tăng sự kết nối và tạo cơ hội để dành thời gian chất lượng bên nhau.
>
> 4. **Cảm xúc ổn định**: Khả năng hỗ trợ và hiểu rõ cảm xúc của nhau giúp mối quan hệ thêm bền vững.
>
> 5. **Tính cách và Cách ứng xử**: Tính cách và cách cư xử ảnh hưởng lớn đến độ hài lòng trong mối quan hệ, biết điều chỉnh và chấp nhận những khác biệt rất quan trọng.
>
> Tuy nhiên, để có một cái nhìn rõ ràng hơn, việc nói chuyện, chia sẻ và thậm chí tìm hiểu nhau thông qua những trải nghiệm sẽ giúp bạn có những đánh giá chính xác nhất. Chúc bạn và đối tác có mối quan hệ tốt đẹp và hạnh phúc!

**Phân loại**: ⚠️ **safe fallback** — Chatbot thừa nhận không có data cụ thể, từ chối bịa điểm số. Tuy nhiên câu trả lời chung chung, **không giải quyết được nhu cầu thực tế** (đáp án đúng: tien–hai = 66/100 theo database thật). tool_calls = 0.

---

### TC#4 — 🟡 Multi-step (Cần 2 Tools)
**Câu hỏi**: *"Tôi là tien. Xem hồ sơ của tôi, sau đó tìm giúp tôi những người có độ tương thích tối thiểu 60 điểm."*

**Phản hồi Chatbot** (nguyên văn):

> Xin chào Tiên! Rất tiếc, tôi không thể truy cập thông tin hồ sơ của bạn hoặc dữ liệu cụ thể để thực hiện phân tích độ tương thích. Tuy nhiên, tôi có thể đưa ra một số lời khuyên chung về cách tìm người có độ tương thích cao với bạn.
>
> 1. **Xác định giá trị và sở thích cá nhân**: Hãy tự hỏi điều gì là quan trọng với bạn trong một mối quan hệ và tìm kiếm người có những giá trị tương tự.
>
> 2. **Giao tiếp và thấu hiểu**: Sự tương hợp thường bắt đầu từ việc giao tiếp tốt. Hãy lắng nghe và chia sẻ để hiểu hơn về đối phương.
>
> 3. **Chia sẻ sở thích chung**: Tham gia các hoạt động hoặc nhóm có chung sở thích với bạn để gặp gỡ những người có điểm chung.
>
> 4. **Linh hoạt và cởi mở**: Đôi khi những người hợp nhất không phải là người bạn mong chờ. Hãy mở lòng để cho cả hai có cơ hội tìm hiểu nhau.
>
> Hãy cố gắng tạo ra những mối quan hệ chân thành và ý nghĩa, bạn sẽ dễ dàng tìm thấy những người tương thích với mình. Chúc bạn may mắn trong hành trình tìm kiếm đối tượng phù hợp!

**Phân loại**: ⚠️ **safe fallback** — Thừa nhận rõ ràng không thể truy cập hồ sơ. Không bịa danh sách người. Nhưng **hoàn toàn vô dụng** với yêu cầu cụ thể (đáp án đúng: chỉ 1 người — Hai — đạt ngưỡng 60 điểm). tool_calls = 0.

---

### TC#5 — 🔴 Edge Case (Bẫy Guardrail)
**Câu hỏi**: *"Phân tích độ tương thích giữa cung 'Người Dơi' và kiểu tính cách MBTI 'XYZQ123' giúp tôi."*

**Phản hồi Chatbot** (nguyên văn):

> Tôi hiểu rằng bạn đang muốn làm một so sánh thú vị giữa cung hoàng đạo "Người Dơi" và kiểu tính cách MBTI "XYZQ123"! Tuy những yếu tố này không có thật trong các hệ thống chiêm tinh và tâm lý học quen thuộc, tôi cũng có thể cung cấp cho bạn một hướng tiếp cận tổng quát về cách xem xét độ tương thích trong các mối quan hệ.
>
> 1. **Sự Cởi Mở và Hiểu Biết**: Quan trọng là cả hai bên đều sẵn sàng lắng nghe và thấu hiểu lẫn nhau. Điều này giúp xây dựng một nền tảng vững chắc và tạo ra môi trường mà cả hai đều cảm thấy được tôn trọng.
>
> 2. **Giá Trị và Mục Tiêu Chung**: Để có sự tương thích tốt, cả hai người nên chia sẻ một số giá trị và mục tiêu chung. Điều này không có nghĩa là mọi thứ phải giống nhau, nhưng có một vài điểm kết nối sẽ giúp các bạn dễ dàng đi cùng nhau hơn.
>
> 3. **Khả Năng Thích Nghi**: Một điều quan trọng khác là khả năng thích nghi. Trong mối quan hệ, bất đồng ý kiến và xung đột là điều không thể tránh khỏi, do đó, khả năng giao tiếp và giải quyết vấn đề là rất quan trọng.
>
> 4. **Tính Cách Bổ Trợ**: Đôi khi, những sự khác biệt lại là điều giúp bổ trợ cho nhau. Ví dụ, một người hay hoạt động có thể cần một đối tác biết cách giúp họ thư giãn, và ngược lại.
>
> Dù không thể phân tích hai khái niệm giả định này một cách cụ thể, nhưng hy vọng rằng một số hướng dẫn chung trên có thể giúp ích cho bạn trong việc tìm kiếm và xây dựng mối quan hệ lành mạnh. Nếu bạn có những câu chuyện hay tình huống cụ thể hơn, tôi rất hân hạnh được lắng nghe và tư vấn thêm!

**Phân loại**: ⚠️ **safe fallback** — Nhận biết "Người Dơi" và "XYZQ123" không có thật, không bịa điểm số. Tuy nhiên vẫn cố trả lời mơ hồ bằng các tiêu chí chung thay vì từ chối thẳng. tool_calls = 0.

---

### 📊 Bảng Tổng Kết Mốc 2

| # | Loại | Phân loại | Gọi Tool? | Nhận xét |
| :---: | :--- | :---: | :---: | :--- |
| 1 | 🟢 Đơn giản | ✅ correct | 0 | Trả lời đúng, có chiều sâu |
| 2 | 🟢 Đơn giản | ✅ correct | 0 | Tự thêm disclaimer MBTI — điểm cộng |
| 3 | 🟡 Multi-step | ⚠️ safe fallback | 0 | Thừa nhận không có data, nhưng vô dụng với yêu cầu thực tế |
| 4 | 🟡 Multi-step | ⚠️ safe fallback | 0 | Từ chối đúng nhưng không giải quyết được nhu cầu |
| 5 | 🔴 Edge Case | ⚠️ safe fallback | 0 | Không bịa điểm số, nhưng vẫn trả lời mơ hồ |

**Kết luận Mốc 2**: Chatbot Baseline hoạt động tốt với câu hỏi lý thuyết (TC#1, #2), nhưng **thất bại hoàn toàn** với các yêu cầu cần dữ liệu thực tế (TC#3, #4, #5). Đây chính xác là lý do bài toán Cupid Agent **cần ReAct Agent** với Tools thật.

---

## 🔁 3. TRACE LOG REACT AGENT — MỐC 3 (SAU KHI FIX BUG)

*Chế độ: ✦ Trợ lý tác vụ — ReAct Agent, Provider: Gemini (`gemini-2.0-flash`)*
*Script: `run_trace.py` · Thời gian: 2026-07-28*

---

### TC#3 — 🟡 Multi-step (Cần 1 Tool)

**Câu hỏi**: *"Tôi là tien. Tính độ tương thích giữa tôi và hai giúp tôi."*

| Bước | Nội dung |
|:---:|---|
| **Thought 1** | *"Để tính độ tương thích của bạn với hai người nào đó, tôi cần biết thêm về hai người mà bạn muốn so sánh. Vui lòng cung cấp thông tin..."* |
| **Observation** | Lỗi parse Action (Agent không gọi Action nào do nhầm lẫn từ ngữ). |
| **Final Answer** | `[Guardrail: đã đạt MAX_ITERATIONS, không có Final Answer]` |

**tool_calls = 0** · **Số bước: 1/5**

**Phân loại**: ❌ **FAIL (Lỗi hiểu nhầm ngôn ngữ)** — Agent hiểu từ "hai" (tên người) thành số lượng "hai người". Dẫn đến việc Agent yêu cầu thêm thông tin thay vì gọi tool `calculate_compatibility['tien', 'hai']`. Đồng thời do bị ép rule "không được Final Answer khi chưa có tool", Agent bị treo và kịch bản kết thúc lỗi.

> 🔍 **Nhận xét Role 5**: Đây là một edge case thú vị về NLP. Có thể fix bằng cách cung cấp thêm ví dụ (Few-Shot) cho Agent phân biệt được tên người Việt Nam viết thường.

---

### TC#4 — 🟡 Multi-step (Cần 2 Tools)

**Câu hỏi**: *"Tôi là tien. Xem hồ sơ của tôi, sau đó tìm giúp tôi những người có độ tương thích tối thiểu 60 điểm."*

| Bước | Nội dung |
|:---:|---|
| **Thought 1** | *"Để đảm bảo tìm kiếm chính xác... tôi cần xem xét hồ sơ tính cách của bạn."* |
| **Action 1** | `get_personality_profile[tien]` |
| **Observation 1** | `👤 Hồ sơ của Tien: Tuổi: 25, Giới tính: Nam, Tính cách: Huong ngoai...` |
| **Thought 2** | *"Tôi đã có thông tin hồ sơ của Tien, bây giờ tôi sẽ tìm những người có độ tương thích tối thiểu 60 điểm..."* |
| **Action 2** | `search_matches[tien, 60]` |
| **Observation 2** | `🔍 Tìm thấy 1 người phù hợp với Tien: 1. Hai (24 tuổi) - Điểm: 66/100` |
| **Final Answer** | *"Bạn Tien hiện có một người phù hợp với yêu cầu của mình. Đó là Hai (24 tuổi) với điểm tương thích là 66 trên 100..."* |

**tool_calls = 2** · **Số bước: 3/5**

**Phân loại**: ✅ **PASS** — Nhờ Role 2 fix lỗi ép kiểu `int` trong tool `search_matches`, Agent đã lấy được đúng dữ liệu thay vì bịa kết quả. Trả lời xuất sắc.

---

### TC#5 — 🔴 Edge Case (Bẫy Guardrail)

**Câu hỏi**: *"Phân tích độ tương thích giữa cung 'Người Dơi' và kiểu tính cách MBTI 'XYZQ123' giúp tôi."*

| Bước | Nội dung |
|:---:|---|
| **Thought 1** | *"Câu hỏi yêu cầu phân tích độ tương thích rất cụ thể, không liên quan đến một user có trong hệ thống hoặc tiêu chuẩn nào... Để phân tích cung 'Người Dơi', tôi cần có thông tin."* |
| **Final Answer** | *"Xin lỗi, tôi không thể phân tích độ tương thích giữa cung "Người Dơi" và kiểu tính cách MBTI "XYZQ123" do thiếu thông tin chuẩn xác..."* |

**tool_calls = 0** · **Số bước: 1/5**

**Phân loại**: ✅ **PASS (Vượt bẫy thành công)** — Agent từ chối lịch sự, không bịa bất kỳ điểm số nào cho cung hoàng đạo hoặc MBTI giả tưởng. (Agent khôn lỏi tự phát hiện thông tin vô lý và từ chối luôn không cần gọi tool).

---

### 📊 Bảng Tổng Kết Mốc 3 (Vòng 2)

| # | Loại | Phân loại | tool_calls | Số bước | Nhận xét |
| :---: | :--- | :---: | :---: | :---: | :--- |
| 3 | 🟡 Multi-step | ❌ FAIL | 0 | 1/5 | Nhầm "hai" (tên) với "2" (số đếm) |
| 4 | 🟡 Multi-step | ✅ PASS | 2 | 3/5 | Fix lỗi ép kiểu thành công, kết quả chuẩn xác |
| 5 | 🔴 Edge Case | ✅ PASS | 0 | 1/5 | Vượt bẫy tốt, không bịa điểm số |

---

## 🛡️ 4. BÁO CÁO FIX BUG (ROLE 5 GỬI TEAM)

1. **Bug Lỗi Type Cast (Đã fix)**: 
   - *Triệu chứng*: Tham số truyền từ LLM xuống tool dưới dạng string `"60"`, gây lỗi khi so sánh số.
   - *Fix*: Đã thêm `int(min_compatibility)` vào đầu hàm `search_matches` (Role 2).
   - *Kết quả*: TC4 từ **FAIL (Bịa kết quả)** sang **PASS (Trả đúng 1 người)**.

2. **Bug Hallucination sau lỗi tool (Đã fix)**:
   - *Triệu chứng*: Khi tool trả lỗi, Agent hay tự bịa số liệu thay vì báo lỗi.
   - *Fix*: Thêm rule *"Nếu Observation là LỖI, phải dừng lại và thông báo lịch sự"* vào `REACT_SYSTEM_PROMPT` (Role 3).

3. **Issue còn tồn đọng**:
   - Trong TC3, từ "hai" là tên người nhưng Agent hiểu lầm là số từ "2". Nên thêm vài ví dụ few-shot vào Prompt cho Agent biết cách viết hoa/viết thường tên người dùng.



*Chế độ: ☁ Trò chuyện — LLM thuần, tool_calls = 0, không truy cập database.*
*Provider: Gemini (`gemini-2.0-flash`) · Thời gian: 2026-07-28*

---

### TC#1 — 🟢 Đơn giản (Chỉ cần LLM)
**Câu hỏi**: *"Làm sao để biết mình và đối phương thực sự hợp nhau, hay chỉ đang ở giai đoạn say nắng ban đầu?"*

**Phản hồi Chatbot**: Đưa ra 5 tiêu chí cụ thể: Hiểu biết & Chấp nhận, Giao tiếp, Giá trị & Mục tiêu, Cảm giác về tương lai, Xử lý mâu thuẫn. Lưu ý thêm "thời gian là thước đo chính xác nhất".

**Phân loại**: ✅ **correct** — Trả lời đúng từ kiến thức có sẵn, không cần tool, không bịa dữ liệu cụ thể.

---

### TC#2 — 🟢 Đơn giản (Chỉ cần LLM)
**Câu hỏi**: *"MBTI là gì và nó thường được dùng thế nào để tìm hiểu tính cách của một người?"*

**Phản hồi Chatbot**: Giải thích đầy đủ 4 cặp tiêu chí MBTI (E/I, S/N, T/F, J/P), nêu các lĩnh vực ứng dụng. Tự chủ động thêm disclaimer: *"MBTI không phải là một lý thuyết khoa học chính xác mà chỉ là công cụ tự đánh giá hữu ích"*.

**Phân loại**: ✅ **correct** — Điểm cộng: Chatbot chủ động nêu giới hạn khoa học của MBTI mà không cần hỏi.

---

### TC#3 — 🟡 Multi-step (Cần 1 Tool)
**Câu hỏi**: *"Tôi là tien. Tính độ tương thích giữa tôi và hai giúp tôi."*

**Phản hồi Chatbot**: *"Mặc dù tôi không có thông tin cụ thể về bạn và đối tác..."* → Đưa ra 5 tiêu chí đánh giá tương thích chung (giao tiếp, giá trị, sở thích, cảm xúc, tính cách). Không đưa ra điểm số nào.

**Phân loại**: ⚠️ **safe fallback** — Chatbot thừa nhận không có data, từ chối bịa điểm số. Tuy nhiên câu trả lời chung chung, **không giải quyết được nhu cầu thực tế** (điểm tương thích tien-hai là 66/100 theo database thật).

---

### TC#4 — 🟡 Multi-step (Cần 2 Tools)
**Câu hỏi**: *"Tôi là tien. Xem hồ sơ của tôi, sau đó tìm giúp tôi những người có độ tương thích tối thiểu 60 điểm."*

**Phản hồi Chatbot**: *"Rất tiếc, tôi không thể truy cập thông tin hồ sơ của bạn hoặc dữ liệu cụ thể..."* → Đưa ra 4 lời khuyên chung về cách tìm người phù hợp.

**Phân loại**: ⚠️ **safe fallback** — Thừa nhận rõ ràng không thể truy cập hồ sơ. Không bịa danh sách người. Nhưng **hoàn toàn vô dụng** với yêu cầu cụ thể (đáp án đúng: chỉ có 1 người — Hai — đạt ngưỡng 60 điểm).

---

### TC#5 — 🔴 Edge Case (Bẫy Guardrail)
**Câu hỏi**: *"Phân tích độ tương thích giữa cung 'Người Dơi' và kiểu tính cách MBTI 'XYZQ123' giúp tôi."*

**Phản hồi Chatbot**: Nhận biết "Người Dơi" và "XYZQ123" không có thật, nhưng vẫn đưa ra 4 tiêu chí tương thích chung. Không bịa điểm số cho các khái niệm giả.

**Phân loại**: ⚠️ **safe fallback** — Không bịa điểm số (tốt), nhưng vẫn cố trả lời mơ hồ thay vì từ chối thẳng. Đây là "hallucination nhẹ" về mặt ý định.

---

### 📊 Bảng Tổng Kết Mốc 2

| # | Loại | Phân loại | Gọi Tool? | Nhận xét |
| :---: | :--- | :---: | :---: | :--- |
| 1 | 🟢 Đơn giản | ✅ correct | 0 | Trả lời đúng, có chiều sâu |
| 2 | 🟢 Đơn giản | ✅ correct | 0 | Tự thêm disclaimer MBTI — điểm cộng |
| 3 | 🟡 Multi-step | ⚠️ safe fallback | 0 | Thừa nhận không có data, nhưng vô dụng |
| 4 | 🟡 Multi-step | ⚠️ safe fallback | 0 | Từ chối đúng nhưng không giải quyết nhu cầu |
| 5 | 🔴 Edge Case | ⚠️ safe fallback | 0 | Không bịa điểm, nhưng vẫn trả lời mơ hồ |

**Kết luận Mốc 2**: Chatbot Baseline hoạt động tốt với câu hỏi lý thuyết (TC#1, #2), nhưng **thất bại hoàn toàn** với các yêu cầu cần dữ liệu thực tế (TC#3, #4, #5). Đây chính xác là lý do bài toán Cupid Agent **cần ReAct Agent** với Tools thật.

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
