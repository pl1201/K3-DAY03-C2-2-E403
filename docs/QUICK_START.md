# 🚀 HƯỚNG DẪN NHANH - CUPID AGENT (QUICK START)

## ⚡ TÓM TẮT DỰ ÁN
- **Chủ đề**: Cupid Agent - Trợ lý ghép đôi & phân tích tương thích.
- **Trạng thái**: Hoàn thành 100% Role 2 (Tool Engineer).
- **Database**: 30 người dùng thực tế tại `data/users_realistic.json`.
- **Tools**: 6 công cụ hoạt động đầy đủ tại `src/tools.py`.
- **Tests**: 100% PASS tại `tests/test_logic.py` và `tests/test_new_tools.py`.

---

## 🎯 CÁC LỆNH CHẠY DỰ ÁN

```bash
# 1. Chạy test suite kiểm tra công cụ
python tests/test_logic.py
python tests/test_new_tools.py

# 2. Chạy ứng dụng demo ReAct Agent
python src/app.py

# 3. Sinh dữ liệu thực tế mới (tùy chọn)
python scripts/generate_realistic_data.py
```

---

## 📂 THƯ MỤC CHÍNH NÊN XEM
1. [README.md](README.md): Tổng quan bài Lab và Thang điểm.
2. [docs/PHAN_CONG_CONG_VIEC.md](docs/PHAN_CONG_CONG_VIEC.md): Sổ tay thực hành chia theo 5 Roles.
3. [docs/CODELAB.md](docs/CODELAB.md): Hướng dẫn thực hành từng bước LMS.
4. [docs/trace_eval.md](docs/trace_eval.md): Nhật ký suy luận Log Trace và Đánh giá Agentic Fit.
