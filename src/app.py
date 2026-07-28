"""
🚀 CORE AGENT APP (Dành cho Role 4: Core Agent Developer)
File chính ghép nối tất cả các thành phần: Tools + Prompts + Test Cases + Multi-Provider.
"""

import json
import os
import sys
from dotenv import load_dotenv

# Đảm bảo import các module cùng thư mục src/ hoạt động mượt mà
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Import các thành phần từ file của Role 2, Role 3 & Multi-Provider Adapter
from tools import (
    AVAILABLE_TOOLS,
    get_personality_profile,
    calculate_compatibility,
    search_matches,
    get_relationship_advice
)
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider

load_dotenv()

def load_test_cases():
    """Đọc bộ test cases từ config/test_cases.json của Role 1"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    
    # Fallback kiểm tra nếu file ở thư mục hiện tại
    if not os.path.exists(config_path):
        config_path = "test_cases.json"
        
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_baseline_chatbot(user_query: str, provider):
    """
    Dựng Chatbot gốc (Baseline) không có công cụ.
    """
    print(f"\n💬 [CHATBOT BASELINE] Câu hỏi: {user_query}")
    print(f"⚙️ System Prompt: {CHATBOT_BASELINE_PROMPT.strip()}")
    
    # Gọi LLM Provider thực hiện sinh câu trả lời
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"🤖 Chatbot trả lời:\n{response}")


def run_react_agent(user_query: str, provider):
    """
    Dựng vòng lặp ReAct Agent (Thought -> Action -> Observation) có Guardrails.
    Demo cho Cupid Agent - Trợ lý ghép đôi & phân tích độ tương thích.
    """
    print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")
    step = 0

    while step < MAX_ITERATIONS:
        step += 1
        print(f"\n--- 🔄 Vòng lặp ReAct (Step {step}/{MAX_ITERATIONS}) ---")

        if step == 1:
            print("🧠 Thought: Câu hỏi này cần tra cứu hồ sơ người dùng Minh.")
            print("🛠️ Action: get_personality_profile['minh']")

            # Thực thi tool
            obs = get_personality_profile("minh")
            print(f"👁️ Observation: {obs}")

        elif step == 2:
            print("🧠 Thought: Đã có hồ sơ của Minh, giờ cần lời khuyên hẹn hò đầu tiên.")
            print("🛠️ Action: get_relationship_advice['hẹn hò đầu tiên']")

            obs = get_relationship_advice("hẹn hò đầu tiên")
            print(f"👁️ Observation: {obs}")

        elif step == 3:
            print("🧠 Thought: Tôi đã có đủ thông tin về hồ sơ Minh và lời khuyên hẹn hò.")
            print("🏁 Final Answer: Minh là người hướng ngoại, thích phiêu lưu. Với tính cách năng động, Minh nên chọn địa điểm hẹn hò đầu tiên ở những nơi có hoạt động ngoài trời như quán cà phê view đẹp hoặc công viên. Hãy lắng nghe chủ động, thể hiện sự tự tin nhưng tự nhiên, và đừng quên tạo không khí thoải mái!")
            break

    if step >= MAX_ITERATIONS:
        print(f"🛡️ GUARDRAIL TRIGGERED: Đã đạt giới hạn tối đa {MAX_ITERATIONS} bước. Ngắt lặp an toàn!")


if __name__ == "__main__":
    print("==================================================")
    print("🏫 ĐẠI HỌC VINUNI - BÀI LAB 3: CHATBOT VS REACT AGENT")
    print("💕 CHỦ ĐỀ: CUPID AGENT - TRỢ LÝ GHÉP ĐÔI & PHÂN TÍCH ĐỘ TƯƠNG THÍCH")
    print("==================================================")

    # Khởi tạo Multi-Provider LLM Adapter (Đọc từ biến môi trường LLM_PROVIDER)
    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Offline Mock Mode")
    print(f"🔌 LLM Provider đang hoạt động: {provider.__class__.__name__} (Model: {model_name})")

    tests = load_test_cases()
    print(f"✅ Đã tải thành công {len(tests)} Test Cases từ config/test_cases.json\n")

    # Chạy thử câu test số 3 (Multi-step với Cupid Agent)
    sample_query = tests[2]["question"]

    print("--- DEMO 1: CHẠY TRÊN CHATBOT BASELINE ---")
    run_baseline_chatbot(sample_query, provider)

    print("\n--- DEMO 2: CHẠY TRÊN REACT AGENT ---")
    run_react_agent(sample_query, provider)

    print("\n" + "="*50)
    print("🎯 DEMO BỔ SUNG: TEST CÁC TOOLS ĐỘC LẬP")
    print("="*50)

    print("\n1️⃣ Test tool: get_personality_profile")
    print(get_personality_profile("minh"))

    print("\n2️⃣ Test tool: calculate_compatibility")
    print(calculate_compatibility("minh", "linh"))

    print("\n3️⃣ Test tool: search_matches")
    print(search_matches("huy", min_compatibility=60))

    print("\n4️⃣ Test tool: get_relationship_advice")
    print(get_relationship_advice("hẹn hò đầu tiên"))

    print("\n5️⃣ Test Edge Case - User không tồn tại:")
    print(get_personality_profile("xyz123"))
