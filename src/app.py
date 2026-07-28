"""Khung web UI tối giản cho trợ lý AI, chạy hoàn toàn từ file app.py."""

import ast
import concurrent.futures
import json
import os
import re
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from dotenv import load_dotenv


SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

from tools import AVAILABLE_TOOLS  # noqa: E402
from prompts import (  # noqa: E402
    CHATBOT_BASELINE_PROMPT,
    GUARDRAIL_FALLBACK_MESSAGE,
    MAX_ITERATIONS,
    REACT_SYSTEM_PROMPT,
    TIMEOUT_SECONDS,
)
from providers import get_llm_provider  # noqa: E402

load_dotenv()

# Nhận diện "Action: ten_tool[tham_so]" trên MỘT dòng — tránh nuốt nhầm nội
# dung nhiều dòng nếu model lỡ viết thêm giải thích phía sau.
_ACTION_PATTERN = re.compile(r"Action:\s*(\w+)\s*\[(.*?)\]\s*$", re.MULTILINE)
_FINAL_ANSWER_PATTERN = re.compile(r"Final Answer:\s*(.*)", re.DOTALL)
_THOUGHT_PATTERN = re.compile(r"Thought:\s*(.*?)(?:\n(?:Action|Final Answer):|\Z)", re.DOTALL)


def load_test_cases():
    """Đọc bộ test cases từ config/test_cases.json."""
    path = os.path.join(ROOT_DIR, "config", "test_cases.json")
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def run_baseline_chatbot(user_query, provider):
    """Backend Chatbot sẵn sàng để kết nối với giao diện."""
    return provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)


def _parse_tool_args(raw_args):
    """Phân tích chuỗi bên trong Action[...] thành list tham số Python an toàn.

    Dùng ast.literal_eval (không phải eval) nên không có rủi ro thực thi mã
    tuỳ ý dù nội dung đến từ LLM. Nếu model quên quote (viết Action: f[minh]
    thay vì f['minh']), fallback coi cả chuỗi là 1 tham số string thô.
    """
    raw_args = raw_args.strip()
    if not raw_args:
        return []
    try:
        parsed = ast.literal_eval(f"[{raw_args}]")
    except (ValueError, SyntaxError):
        return [raw_args.strip("'\" ")]
    return list(parsed) if isinstance(parsed, (list, tuple)) else [parsed]


def _call_tool(action_name, args):
    """Gọi tool theo tên. KHÔNG BAO GIỜ để exception lọt ra ngoài vòng lặp.

    Đây là phanh guardrail thứ hai độc lập với tools.py: kể cả nếu một tool
    tự crash (vd. truyền sai kiểu tham số), Agent vẫn tiếp tục thay vì sập.
    """
    tool = AVAILABLE_TOOLS.get(action_name)
    if tool is None:
        available = ", ".join(sorted(AVAILABLE_TOOLS))
        return f"LỖI: Không tìm thấy tool '{action_name}'. Các tool hợp lệ: {available}."
    try:
        return tool(*args)
    except Exception as exc:  # noqa: BLE001 - phòng thủ có chủ đích, xem docstring
        return f"LỖI: Tool '{action_name}' gặp sự cố khi chạy với tham số {args}: {exc}"


def _generate_with_timeout(provider, prompt, system_prompt, timeout_seconds):
    """Gọi provider.generate() với giới hạn thời gian — phanh chống treo vô hạn."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(provider.generate, prompt, system_prompt)
        try:
            return future.result(timeout=timeout_seconds)
        except concurrent.futures.TimeoutError:
            return (
                f"LỖI: Provider không phản hồi sau {timeout_seconds}s "
                f"(timeout guardrail, không phải lỗi Final Answer)."
            )


def run_react_agent(user_query, provider):
    """Vòng lặp ReAct tổng quát: Thought -> Action -> Observation -> lặp lại.

    Không hardcode kịch bản cho bất kỳ câu hỏi cụ thể nào. App (không phải
    LLM) là bên duy nhất chèn Observation, đúng "nguyên tắc bất biến #2" của
    CODELAB.md. Có 3 lớp Guardrail độc lập:
      1. MAX_ITERATIONS  - chặn lặp vô hạn nếu Agent không bao giờ kết luận.
      2. repeated_action  - dừng SỚM nếu Agent lặp lại đúng 1 Action (Agent
         "bí" và cứ thử lại y hệt) thay vì chờ hết MAX_ITERATIONS.
      3. _call_tool try/except - tool tự crash không làm sập cả Agent.
    """
    scratchpad = ""
    trace = []
    last_action_signature = None

    for step in range(1, MAX_ITERATIONS + 1):
        prompt = user_query if not scratchpad else f"{user_query}\n\n{scratchpad}"
        raw_response = _generate_with_timeout(
            provider, prompt, REACT_SYSTEM_PROMPT, TIMEOUT_SECONDS
        )

        action_match = _ACTION_PATTERN.search(raw_response)
        final_match = _FINAL_ANSWER_PATTERN.search(raw_response)
        thought_match = _THOUGHT_PATTERN.search(raw_response)
        thought = thought_match.group(1).strip() if thought_match else None

        # Nếu cả hai xuất hiện (model lẫn lộn), ưu tiên cái đứng trước trong văn bản.
        if final_match and (action_match is None or final_match.start() < action_match.start()):
            answer = final_match.group(1).strip()
            trace.append({
                "step": step, "type": "final_answer",
                "thought": thought, "answer": answer,
            })
            return {"answer": answer, "steps": trace, "stopped_reason": "final_answer"}

        if action_match is None:
            # Model không tuân thủ định dạng bắt buộc — vẫn tính 1 lượt vào
            # MAX_ITERATIONS để không biến thành vòng lặp vô hạn trá hình.
            trace.append({"step": step, "type": "malformed", "raw_response": raw_response})
            scratchpad += (
                f"\n{raw_response}\n"
                "Observation: LỖI ĐỊNH DẠNG - Bạn PHẢI trả lời đúng mẫu "
                "'Thought: ...' rồi 'Action: ten_tool[tham_so]' hoặc "
                "'Thought: ...' rồi 'Final Answer: ...'.\n"
            )
            continue

        action_name = action_match.group(1)
        args = _parse_tool_args(action_match.group(2))
        action_signature = (action_name, tuple(str(a) for a in args))

        if action_signature == last_action_signature:
            trace.append({
                "step": step, "type": "guardrail_stop", "reason": "repeated_action",
                "action": action_name, "args": args,
            })
            return {
                "answer": GUARDRAIL_FALLBACK_MESSAGE,
                "steps": trace,
                "stopped_reason": "repeated_action",
            }
        last_action_signature = action_signature

        observation = _call_tool(action_name, args)
        trace.append({
            "step": step, "type": "action", "thought": thought,
            "action": action_name, "args": args, "observation": observation,
        })
        scratchpad += (
            f"\nThought: {thought or ''}\nAction: {action_name}{args}\n"
            f"Observation: {observation}\n"
        )

    trace.append({"step": MAX_ITERATIONS + 1, "type": "guardrail_stop", "reason": "max_iterations"})
    return {
        "answer": GUARDRAIL_FALLBACK_MESSAGE,
        "steps": trace,
        "stopped_reason": "max_iterations",
    }


HTML = r"""<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Mây Tình Cảm — Cupid Agent</title>
  <style>
    :root {
      --ink:#1d2822; --muted:#6c7771; --paper:#f5f6f1; --white:#fff;
      --night:#202a25; --night-2:#2b3832; --line:#dce1d9;
      --orange:#d96c47; --orange-2:#c65c3b; --lime:#dce8c9;
      --soft:#edf0e9; --shadow:0 18px 45px rgba(36,49,42,.08);
    }
    * { box-sizing:border-box; }
    body {
      margin:0; min-height:100vh; background:var(--paper); color:var(--ink);
      font-family:"Segoe UI",Inter,Arial,sans-serif; overflow:hidden;
    }
    button,textarea { font:inherit; }
    button { cursor:pointer; }
    .app { display:grid; grid-template-columns:250px 1fr; height:100vh; }
    aside {
      background:var(--night); color:white; padding:25px 18px 20px;
      display:flex; flex-direction:column;
    }
    .brand { display:flex; align-items:center; gap:11px; padding:0 5px 23px; }
    .logo {
      width:39px; height:39px; border-radius:50%; display:grid; place-items:center;
      background:var(--orange); font:700 19px Georgia,serif;
    }
    .brand strong { display:block; font:700 19px Georgia,serif; }
    .brand small { color:#aebbb4; font-size:11px; }
    .new-chat {
      border:0; border-radius:10px; padding:13px 14px; text-align:left;
      color:white; background:var(--orange); font-weight:650;
      transition:.2s ease;
    }
    .new-chat:hover { background:var(--orange-2); transform:translateY(-1px); }
    .profile-button {
      margin-top:9px; border:1px solid #435149; border-radius:10px;
      padding:12px 14px; color:#e8eee9; background:transparent;
      text-align:left; font-weight:650; transition:.2s ease;
    }
    .profile-button:hover { background:var(--night-2); border-color:#607168; }
    .section-title {
      margin:27px 9px 10px; color:#84938b; font-size:10px;
      font-weight:700; letter-spacing:.12em;
    }
    #history { flex:1; }
    .history-empty { color:#718079; font-size:13px; padding:10px 9px; }
    .history-item {
      width:100%; border:0; border-radius:8px; padding:10px; color:#d6ded9;
      background:transparent; text-align:left; white-space:nowrap; overflow:hidden;
      text-overflow:ellipsis; font-size:13px;
    }
    .history-item:hover { background:var(--night-2); }
    .profile {
      border-top:1px solid #34413b; padding:17px 5px 0;
      display:flex; align-items:center; gap:10px;
    }
    .avatar {
      width:34px; height:34px; border-radius:9px; display:grid; place-items:center;
      background:var(--lime); color:var(--ink); font-weight:750;
    }
    .profile-copy { flex:1; }
    .profile-copy strong { display:block; font-size:13px; }
    .profile-copy small { color:#8fa097; font-size:11px; }
    .online { color:#91c788; font-size:10px; }
    main { display:grid; grid-template-rows:72px 1fr auto; min-width:0; }
    header {
      display:flex; align-items:center; justify-content:space-between;
      padding:0 36px; border-bottom:1px solid rgba(220,225,217,.7);
    }
    .modes { display:flex; gap:3px; padding:4px; border-radius:11px; background:var(--soft); }
    .mode {
      border:0; border-radius:8px; padding:9px 14px; color:var(--muted);
      background:transparent; font-size:13px; font-weight:650;
    }
    .mode.active { background:white; color:var(--ink); box-shadow:0 2px 8px rgba(0,0,0,.05); }
    .status { color:var(--muted); font-size:12px; }
    .status::before { content:""; display:inline-block; width:7px; height:7px;
      margin-right:7px; border-radius:50%; background:#7eb879; }
    .stage { min-height:0; position:relative; overflow:hidden; }
    .welcome {
      height:100%; display:flex; flex-direction:column; align-items:center;
      justify-content:center; padding-bottom:4vh;
    }
    h1 { margin:0; font:700 clamp(34px,4vw,48px) Georgia,serif; letter-spacing:-.035em; }
    .lead { margin:12px 0 34px; color:var(--muted); font-size:15px; }
    .cards { display:flex; gap:13px; }
    .card {
      width:190px; min-height:124px; padding:16px; border:1px solid var(--line);
      border-radius:16px; background:white; text-align:left; color:var(--ink);
      transition:.22s ease; box-shadow:0 7px 25px rgba(45,59,52,.025);
    }
    .card:hover { transform:translateY(-4px); border-color:#c8d0c5; box-shadow:var(--shadow); }
    .card-icon {
      display:grid; place-items:center; width:34px; height:29px; border-radius:9px;
      margin-bottom:12px; background:var(--lime); font-weight:800;
    }
    .card strong { display:block; font-size:14px; }
    .card small { display:block; margin-top:5px; color:var(--muted); }
    .trust-note {
      display:flex; align-items:flex-start; gap:9px; max-width:600px;
      margin-top:25px; padding:11px 14px; border-radius:12px;
      background:#eef2e8; color:var(--muted); font-size:11px; line-height:1.5;
    }
    .chat {
      display:none; position:absolute; inset:0; overflow-y:auto; overflow-x:hidden;
      padding:35px max(35px,calc((100% - 760px)/2)) 52px;
      overscroll-behavior:contain; scrollbar-gutter:stable;
      scroll-behavior:smooth;
    }
    .chat::-webkit-scrollbar { width:9px; }
    .chat::-webkit-scrollbar-track { background:transparent; }
    .chat::-webkit-scrollbar-thumb {
      background:#cbd2ca; border:2px solid var(--paper); border-radius:99px;
    }
    .chat::-webkit-scrollbar-thumb:hover { background:#aeb9af; }
    .message { display:flex; margin-bottom:22px; animation:arrive .3s ease both; }
    .message.user { justify-content:flex-end; }
    .bubble {
      max-width:75%; padding:13px 17px; border-radius:16px; line-height:1.55;
      font-size:14px; white-space:pre-wrap; overflow-wrap:anywhere;
    }
    .user .bubble { color:white; background:#263a31; border-bottom-right-radius:4px; }
    .assistant { gap:11px; align-items:flex-start; }
    .assistant .bubble {
      background:white; border:1px solid var(--line); border-top-left-radius:4px;
      box-shadow:0 8px 25px rgba(36,49,42,.045);
    }
    .mini-logo {
      flex:0 0 31px; width:31px; height:31px; display:grid; place-items:center;
      border-radius:50%; color:white; background:var(--orange); font:700 14px Georgia,serif;
    }
    .trace {
      margin-top:9px; border:1px solid var(--line); border-radius:11px;
      background:var(--soft); font-size:12px; overflow:hidden;
    }
    .trace summary {
      padding:8px 12px; cursor:pointer; color:var(--muted); font-weight:650;
      list-style:none;
    }
    .trace summary::-webkit-details-marker { display:none; }
    .trace-step {
      padding:7px 12px; border-top:1px solid var(--line);
      font-family:Consolas,"SF Mono",monospace; white-space:pre-wrap;
      line-height:1.5; color:var(--ink);
    }
    .trace-step b { color:var(--orange-2); }
    .result-card {
      margin-top:10px; padding:13px; border-radius:12px;
      background:linear-gradient(135deg,#fff7f2,#f1f6e9); border:1px solid #eadfd7;
    }
    .result-top { display:flex; align-items:center; justify-content:space-between; gap:12px; }
    .result-top strong { font-family:Georgia,serif; font-size:15px; }
    .score-pill {
      flex:0 0 auto; padding:5px 9px; border-radius:999px;
      color:#8d3f28; background:#f7d9ce; font-size:12px; font-weight:750;
    }
    .result-note { margin:8px 0 0; color:var(--muted); font-size:11px; line-height:1.45; }
    .modal {
      position:fixed; inset:0; z-index:20; display:none; place-items:center;
      padding:20px; background:rgba(19,30,24,.58); backdrop-filter:blur(5px);
    }
    .modal.open { display:grid; animation:fadeIn .2s ease; }
    .dialog {
      width:min(540px,100%); border-radius:20px; background:white;
      box-shadow:0 28px 90px rgba(15,25,19,.28); overflow:hidden;
    }
    .dialog-head { display:flex; justify-content:space-between; padding:22px 24px 14px; }
    .dialog-head h2 { margin:0; font:700 23px Georgia,serif; }
    .dialog-head p { margin:6px 0 0; color:var(--muted); font-size:12px; }
    .close {
      width:34px; height:34px; border:0; border-radius:50%; color:var(--muted);
      background:var(--soft); font-size:18px;
    }
    .progress { display:flex; gap:6px; padding:0 24px 20px; }
    .progress span { height:4px; flex:1; border-radius:99px; background:var(--line); }
    .progress span.active { background:var(--orange); }
    .wizard-step { display:none; padding:0 24px 8px; }
    .wizard-step.active { display:block; }
    .wizard-step h3 { margin:0 0 16px; font-size:16px; }
    .field { display:block; margin-bottom:15px; }
    .field span { display:block; margin-bottom:7px; color:var(--muted); font-size:12px; font-weight:650; }
    .field input,.field select {
      width:100%; border:1px solid var(--line); border-radius:11px;
      padding:11px 12px; outline:0; color:var(--ink); background:white;
    }
    .field input:focus,.field select:focus { border-color:#9daf9f; }
    .privacy-box {
      margin:7px 24px 0; padding:11px 13px; border-radius:11px;
      color:#536159; background:#eef2e8; font-size:11px; line-height:1.5;
    }
    .dialog-actions {
      display:flex; justify-content:space-between; gap:10px; padding:19px 24px 23px;
    }
    .secondary,.primary {
      border:0; border-radius:10px; padding:10px 16px; font-weight:700;
    }
    .secondary { color:var(--muted); background:var(--soft); }
    .primary { margin-left:auto; color:white; background:var(--orange); }
    @keyframes fadeIn { from { opacity:0; } }
    .composer-wrap { padding:8px max(36px,calc((100% - 790px)/2)) 22px; }
    .composer {
      display:grid; grid-template-columns:1fr 46px; align-items:end; padding:8px 9px 8px 5px;
      border:1px solid var(--line); border-radius:16px; background:white;
      box-shadow:0 10px 32px rgba(36,49,42,.06); transition:.2s;
    }
    .composer:focus-within { border-color:#aab8ad; box-shadow:0 14px 38px rgba(36,49,42,.1); }
    textarea {
      width:100%; max-height:130px; resize:none; border:0; outline:0; padding:11px 13px;
      color:var(--ink); background:transparent; line-height:1.45;
      overflow-y:hidden; scrollbar-width:thin;
    }
    textarea.input-scroll { overflow-y:auto; }
    textarea::placeholder { color:#8c9690; }
    .send {
      width:42px; height:42px; border:0; border-radius:11px; color:white;
      background:var(--orange); font-size:20px; transition:.2s;
    }
    .send:hover { background:var(--orange-2); transform:scale(1.04); }
    .hint { margin:7px 0 0; color:#8c9690; text-align:center; font-size:10px; }
    @keyframes arrive { from { opacity:0; transform:translateY(8px); } }
    @media (max-width:820px) {
      .app { grid-template-columns:76px 1fr; }
      aside { padding:22px 12px; align-items:center; }
      .brand-copy,.new-label,.profile-label,.section-title,#history,.profile-copy,.online { display:none; }
      .brand { padding:0 0 24px; }
      .new-chat { width:44px; height:44px; padding:0; text-align:center; font-size:20px; }
      .profile-button { width:44px; height:44px; padding:0; text-align:center; font-size:18px; }
      .profile { padding:18px 0 0; }
      .cards { flex-wrap:wrap; justify-content:center; }
      .card { width:165px; }
      header { padding:0 18px; }
      .status { display:none; }
    }
    @media (max-width:560px) {
      .app { grid-template-columns:1fr; }
      aside { display:none; }
      .card { width:145px; }
      .welcome { justify-content:flex-start; padding-top:15vh; }
      .lead { margin-bottom:25px; text-align:center; }
      .composer-wrap { padding:8px 14px 15px; }
    }
  </style>
</head>
<body>
<div class="app">
  <aside>
    <div class="brand">
      <div class="logo">♥</div>
      <div class="brand-copy"><strong>Mây</strong><small>Cupid Agent</small></div>
    </div>
    <button class="new-chat" onclick="newChat()">＋ <span class="new-label">&nbsp;Cuộc trò chuyện mới</span></button>
    <button class="profile-button" onclick="openProfile()">♡ <span class="profile-label">&nbsp;Hồ sơ của tôi</span></button>
    <div class="section-title">GẦN ĐÂY</div>
    <div id="history"><div class="history-empty">Chưa có cuộc trò chuyện</div></div>
    <div class="profile">
      <div class="avatar">B</div>
      <div class="profile-copy"><strong>Bạn</strong><small>Sẵn sàng</small></div>
      <span class="online">●</span>
    </div>
  </aside>
  <main>
    <header>
      <div class="modes">
        <button class="mode active" data-mode="chat" onclick="setMode(this)">☁&nbsp; Tư vấn</button>
        <button class="mode" data-mode="agent" onclick="setMode(this)">♥&nbsp; Ghép đôi</button>
      </div>
      <div class="status">Hệ thống sẵn sàng</div>
    </header>
    <section class="stage">
      <div class="welcome" id="welcome">
        <h1>Chuyện tình cảm, để Mây cùng bạn</h1>
        <p class="lead">Tìm sự đồng điệu bằng dữ liệu, trò chuyện bằng sự thấu hiểu.</p>
        <div class="cards">
          <button class="card" onclick="agentSuggest('Tìm người phù hợp với tien, điểm tương thích tối thiểu 60')">
            <span class="card-icon">♥</span><strong>Tìm người phù hợp</strong><small>Khám phá kết nối mới</small>
          </button>
          <button class="card" onclick="agentSuggest('Tính độ tương thích giữa tien và hai giúp tôi')">
            <span class="card-icon">⇄</span><strong>So sánh hồ sơ</strong><small>Nhìn rõ điểm chung</small>
          </button>
          <button class="card" onclick="agentSuggest('Xem hồ sơ của tien và phân tích độ tương thích với hai')">
            <span class="card-icon">✦</span><strong>Xem tương thích</strong><small>Điểm số có giải thích</small>
          </button>
          <button class="card" onclick="suggest('Cho tôi lời khuyên để xây dựng một mối quan hệ lành mạnh')">
            <span class="card-icon">☁</span><strong>Xin lời khuyên</strong><small>Một góc nhìn ấm áp</small>
          </button>
        </div>
        <div class="trust-note">
          <span>ⓘ</span>
          <span>MBTI và cung hoàng đạo chỉ mang tính tham khảo. Mây không hiển thị thông tin riêng tư của người khác và không thay bạn đưa ra quyết định tình cảm.</span>
        </div>
      </div>
      <div class="chat" id="chat"></div>
    </section>
    <div class="composer-wrap">
      <div class="composer">
        <textarea id="input" rows="1" placeholder="Bạn muốn tìm hiểu điều gì về một kết nối?"></textarea>
        <button class="send" onclick="send()" aria-label="Gửi">➜</button>
      </div>
      <p class="hint">Enter để gửi · Shift + Enter để xuống dòng</p>
    </div>
  </main>
</div>
<div class="modal" id="profileModal" role="dialog" aria-modal="true" aria-labelledby="profileTitle">
  <div class="dialog">
    <div class="dialog-head">
      <div><h2 id="profileTitle">Hồ sơ của bạn</h2><p>Ba bước ngắn để Mây hiểu bạn hơn</p></div>
      <button class="close" onclick="closeProfile()" aria-label="Đóng">×</button>
    </div>
    <div class="progress"><span class="active"></span><span></span><span></span></div>
    <div class="wizard-step active" data-step="0">
      <h3>Trước tiên, một chút về bạn</h3>
      <label class="field"><span>Tên gọi</span><input id="profileName" maxlength="30" placeholder="Ví dụ: An"></label>
      <label class="field"><span>Tuổi</span><input id="profileAge" type="number" min="18" max="100" placeholder="Từ 18 tuổi"></label>
    </div>
    <div class="wizard-step" data-step="1">
      <h3>Cách bạn nhìn về bản thân</h3>
      <label class="field"><span>MBTI (không bắt buộc)</span>
        <select id="profileMbti"><option value="">Chưa rõ</option><option>INTJ</option><option>INTP</option><option>ENTJ</option><option>ENTP</option><option>INFJ</option><option>INFP</option><option>ENFJ</option><option>ENFP</option><option>ISTJ</option><option>ISFJ</option><option>ESTJ</option><option>ESFJ</option><option>ISTP</option><option>ISFP</option><option>ESTP</option><option>ESFP</option></select>
      </label>
      <label class="field"><span>Cung hoàng đạo (không bắt buộc)</span>
        <select id="profileZodiac"><option value="">Chưa rõ</option><option>Bạch Dương</option><option>Kim Ngưu</option><option>Song Tử</option><option>Cự Giải</option><option>Sư Tử</option><option>Xử Nữ</option><option>Thiên Bình</option><option>Bọ Cạp</option><option>Nhân Mã</option><option>Ma Kết</option><option>Bảo Bình</option><option>Song Ngư</option></select>
      </label>
    </div>
    <div class="wizard-step" data-step="2">
      <h3>Điều làm bạn thấy kết nối</h3>
      <label class="field"><span>Sở thích</span><input id="profileInterests" maxlength="120" placeholder="Ví dụ: đọc sách, du lịch, nấu ăn"></label>
      <label class="field"><span>Bạn đang tìm kiếm</span>
        <select id="profileGoal"><option>Một mối quan hệ nghiêm túc</option><option>Người đồng hành phù hợp</option><option>Lời khuyên tình cảm</option><option>Mở rộng kết nối</option></select>
      </label>
    </div>
    <div class="privacy-box">🔒 Thông tin này chỉ được dùng trong phiên trò chuyện hiện tại. Không nhập số điện thoại, địa chỉ hoặc thông tin nhận dạng nhạy cảm.</div>
    <div class="dialog-actions">
      <button class="secondary" id="backButton" onclick="wizardBack()" style="visibility:hidden">Quay lại</button>
      <button class="primary" id="nextButton" onclick="wizardNext()">Tiếp tục</button>
    </div>
  </div>
</div>
<script>
  const input = document.querySelector('#input');
  const chat = document.querySelector('#chat');
  const welcome = document.querySelector('#welcome');
  const historyBox = document.querySelector('#history');
  const profileModal = document.querySelector('#profileModal');
  let mode = 'chat', started = false, sending = false, history = [], wizardStep = 0;

  function setMode(button) {
    document.querySelectorAll('.mode').forEach(el => el.classList.remove('active'));
    button.classList.add('active'); mode = button.dataset.mode;
  }
  function suggest(text) { input.value = text; resize(); input.focus(); }
  function agentSuggest(text) {
    mode = 'agent';
    document.querySelectorAll('.mode').forEach(el =>
      el.classList.toggle('active', el.dataset.mode === 'agent'));
    suggest(text);
  }
  function resize() {
    input.style.height = 'auto';
    const nextHeight = Math.min(input.scrollHeight,130);
    input.style.height = nextHeight+'px';
    input.classList.toggle('input-scroll', input.scrollHeight > 130);
  }
  input.addEventListener('input', resize);
  input.addEventListener('keydown', event => {
    if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); send(); }
  });
  function start(text) {
    if (started) return;
    started = true; welcome.style.display = 'none'; chat.style.display = 'block';
    history.unshift(text.length > 28 ? text.slice(0,28)+'…' : text); renderHistory();
  }
  function addMessage(text, who) {
    const row = document.createElement('div'); row.className = 'message '+who;
    if (who === 'assistant') {
      const logo = document.createElement('div'); logo.className='mini-logo'; logo.textContent='M';
      row.appendChild(logo);
    }
    const bubble = document.createElement('div'); bubble.className='bubble'; bubble.textContent=text;
    row.appendChild(bubble); chat.appendChild(row);
    requestAnimationFrame(() => chat.scrollTo({top:chat.scrollHeight,behavior:'smooth'}));
    return bubble;
  }
  function renderTrace(bubble, steps) {
    if (!steps || !steps.length) return;
    const box = document.createElement('details'); box.className='trace';
    const summary = document.createElement('summary');
    summary.textContent = '✓ Mây đã thực hiện ' + steps.length + ' bước';
    box.appendChild(summary);
    const actionLabels = {
      get_personality_profile:'Đã kiểm tra hồ sơ',
      calculate_compatibility:'Đã tính độ tương thích',
      search_matches:'Đã tìm người phù hợp',
      get_relationship_advice:'Đã tham khảo lời khuyên',
      get_zodiac_compatibility:'Đã đối chiếu cung hoàng đạo',
      get_mbti_compatibility:'Đã đối chiếu MBTI'
    };
    steps.forEach(step => {
      const div = document.createElement('div'); div.className='trace-step';
      if (step.type === 'action') {
        div.innerHTML = '<b>✓</b> ' + escapeHtml(actionLabels[step.action] || 'Đã kiểm tra thông tin');
      } else if (step.type === 'final_answer') {
        div.innerHTML = '<b>✓</b> Đã tổng hợp kết quả';
      } else if (step.type === 'guardrail_stop') {
        div.innerHTML = '<b>⛔</b> Đã dừng an toàn vì chưa đủ dữ liệu đáng tin cậy';
      } else {
        div.innerHTML = '<b>↻</b> Đã thử lại một bước chưa hoàn chỉnh';
      }
      box.appendChild(div);
    });
    bubble.parentElement.appendChild(box);
    requestAnimationFrame(() => chat.scrollTo({top:chat.scrollHeight,behavior:'smooth'}));
  }
  function renderResult(bubble, answer) {
    const score = String(answer).match(/(\d{1,3}(?:[.,]\d+)?)\s*\/\s*100/);
    const card = document.createElement('div'); card.className='result-card';
    const top = document.createElement('div'); top.className='result-top';
    const title = document.createElement('strong'); title.textContent='Góc nhìn tương thích';
    top.appendChild(title);
    if (score) {
      const pill = document.createElement('span'); pill.className='score-pill';
      pill.textContent=score[1] + '/100'; top.appendChild(pill);
    }
    const note = document.createElement('p'); note.className='result-note';
    note.textContent='Kết quả là gợi ý dựa trên dữ liệu hiện có, không phải kết luận về một mối quan hệ.';
    card.appendChild(top); card.appendChild(note); bubble.appendChild(card);
  }
  function escapeHtml(text) {
    const div = document.createElement('div'); div.textContent = String(text); return div.innerHTML;
  }
  async function send() {
    const text=input.value.trim(); if (!text || sending) return;
    start(text); addMessage(text,'user'); input.value=''; resize();
    sending = true;
    const bubble = addMessage('Đang suy nghĩ…', 'assistant');
    try {
      const response = await fetch('/api/chat', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({message:text, mode})
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Không thể kết nối');
      bubble.textContent = data.answer || 'Không có phản hồi từ máy chủ.';
      if (mode === 'agent') {
        renderResult(bubble, data.answer);
        renderTrace(bubble, data.steps);
      }
    } catch (error) {
      bubble.textContent = 'Mình chưa thể trả lời lúc này. Bạn thử lại sau một chút nhé.';
      console.error(error);
    } finally {
      sending = false; input.focus();
    }
  }
  function renderHistory() {
    historyBox.innerHTML='';
    history.slice(0,6).forEach(title => {
      const el=document.createElement('button'); el.className='history-item';
      el.textContent='◌  '+title; historyBox.appendChild(el);
    });
  }
  function newChat() {
    started=false; chat.innerHTML=''; chat.style.display='none'; welcome.style.display='flex';
    input.value=''; resize(); input.focus();
  }
  function openProfile() {
    wizardStep=0; updateWizard(); profileModal.classList.add('open');
    document.querySelector('#profileName').focus();
  }
  function closeProfile() { profileModal.classList.remove('open'); }
  function updateWizard() {
    document.querySelectorAll('.wizard-step').forEach((el,index) =>
      el.classList.toggle('active', index === wizardStep));
    document.querySelectorAll('.progress span').forEach((el,index) =>
      el.classList.toggle('active', index <= wizardStep));
    document.querySelector('#backButton').style.visibility = wizardStep ? 'visible' : 'hidden';
    document.querySelector('#nextButton').textContent = wizardStep === 2 ? 'Hoàn tất' : 'Tiếp tục';
  }
  function wizardBack() { if (wizardStep > 0) { wizardStep--; updateWizard(); } }
  function wizardNext() {
    if (wizardStep === 0) {
      const age=Number(document.querySelector('#profileAge').value);
      if (!age || age < 18) {
        document.querySelector('#profileAge').focus();
        document.querySelector('#profileAge').setCustomValidity('Bạn cần đủ 18 tuổi để sử dụng tính năng ghép đôi.');
        document.querySelector('#profileAge').reportValidity();
        return;
      }
      document.querySelector('#profileAge').setCustomValidity('');
    }
    if (wizardStep < 2) { wizardStep++; updateWizard(); return; }
    const name=document.querySelector('#profileName').value.trim() || 'mình';
    const mbti=document.querySelector('#profileMbti').value;
    const zodiac=document.querySelector('#profileZodiac').value;
    const interests=document.querySelector('#profileInterests').value.trim();
    const goal=document.querySelector('#profileGoal').value;
    const details=[mbti && 'MBTI '+mbti,zodiac && 'cung '+zodiac,interests && 'thích '+interests]
      .filter(Boolean).join(', ');
    closeProfile();
    suggest('Tôi là '+name+(details ? ', '+details : '')+'. Tôi đang tìm '+goal.toLowerCase()+'. Hãy cho tôi một gợi ý phù hợp.');
  }
  profileModal.addEventListener('click', event => {
    if (event.target === profileModal) closeProfile();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') closeProfile();
  });
  input.focus();
</script>
</body>
</html>
"""


class AppHandler(BaseHTTPRequestHandler):
    provider = None

    def do_GET(self):
        if self.path not in ("/", "/index.html"):
            self.send_error(404)
            return
        body = HTML.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
            # Trình duyệt đã đóng hoặc tải lại trang trước khi gửi xong.
            return

    def do_POST(self):
        if self.path != "/api/chat":
            self.send_error(404)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0 or content_length > 20_000:
                self._send_json({"error": "Nội dung yêu cầu không hợp lệ."}, status=400)
                return

            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
            user_query = str(payload.get("message", "")).strip()
            mode = payload.get("mode") or "chat"
            if not user_query:
                self._send_json({"error": "Bạn chưa nhập câu hỏi."}, status=400)
                return

            if AppHandler.provider is None:
                AppHandler.provider = get_llm_provider()

            if mode == "agent":
                result = run_react_agent(user_query, AppHandler.provider)
                self._send_json({
                    "answer": result["answer"],
                    "steps": result["steps"],
                    "stopped_reason": result["stopped_reason"],
                    "mode": "agent",
                    "provider": AppHandler.provider.__class__.__name__,
                })
            else:
                answer = run_baseline_chatbot(user_query, AppHandler.provider)
                self._send_json({
                    "answer": answer,
                    "steps": [],
                    "mode": "chat",
                    "provider": AppHandler.provider.__class__.__name__,
                    "model": getattr(AppHandler.provider, "model_name", "offline-mock"),
                })
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json({"error": "Dữ liệu gửi lên không đúng định dạng."}, status=400)
        except Exception as error:  # noqa: BLE001 - phòng thủ có chủ đích: 1 request lỗi không được làm sập server
            print(f"Lỗi khi xử lý /api/chat: {error}")
            self._send_json({"error": "Hệ thống đang bận, vui lòng thử lại."}, status=500)

    def _send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
            # Người dùng có thể refresh hoặc đóng tab trong lúc model xử lý.
            return False
        return True

    def log_message(self, format_string, *args):
        return


def main(host="127.0.0.1", port=8000, open_browser=True):
    server = ThreadingHTTPServer((host, port), AppHandler)
    url = f"http://{host}:{port}"
    print(f"Mây đang chạy tại {url}")
    print("Nhấn Ctrl+C để dừng.")
    if open_browser:
        threading.Timer(0.7, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng Mây.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
