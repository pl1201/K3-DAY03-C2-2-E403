"""Script chạy ReAct Agent trực tiếp qua tools thật để lấy trace log Mốc 3."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tools import (
    get_personality_profile, calculate_compatibility,
    search_matches, get_zodiac_compatibility, get_mbti_compatibility,
    AVAILABLE_TOOLS
)
from prompts import REACT_SYSTEM_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider
import re

provider = get_llm_provider()

def parse_action(text):
    """Parse Action: tool_name[args] từ LLM output."""
    match = re.search(r'Action:\s*(\w+)\[(.+?)\]', text, re.DOTALL)
    if not match:
        return None, None
    tool_name = match.group(1).strip()
    args_raw = match.group(2).strip()
    # Parse args
    args = [a.strip().strip("'\"") for a in args_raw.split(',')]
    return tool_name, args

def parse_final_answer(text):
    match = re.search(r'Final Answer:\s*(.+)', text, re.DOTALL)
    return match.group(1).strip() if match else None

def run_react_trace(question, label=""):
    print(f"\n{'='*60}")
    print(f"🧪 {label}")
    print(f"❓ Câu hỏi: {question}")
    print('='*60)

    history = f"Question: {question}\n"
    trace_steps = []
    final_answer = None

    for step in range(1, MAX_ITERATIONS + 1):
        prompt = REACT_SYSTEM_PROMPT + "\n" + history
        llm_output = provider.generate(prompt)
        print(f"\n--- Vòng lặp ReAct (Step {step}/{MAX_ITERATIONS}) ---")
        print(f"[LLM RAW OUTPUT]:\n{llm_output}")

        # Tách Thought
        thought_match = re.search(r'Thought:\s*(.+?)(?=\nAction:|\nFinal Answer:|$)', llm_output, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else "(không tìm thấy Thought)"

        # Kiểm tra Final Answer trước
        fa = parse_final_answer(llm_output)
        if fa:
            print(f"🧠 Thought: {thought}")
            print(f"🏁 Final Answer: {fa}")
            trace_steps.append({"step": step, "thought": thought, "final_answer": fa})
            final_answer = fa
            break

        # Parse Action
        tool_name, args = parse_action(llm_output)
        if not tool_name:
            print(f"⚠️ Không parse được Action ở step {step}. Kết thúc sớm.")
            trace_steps.append({"step": step, "thought": thought, "error": "parse_failed"})
            break

        # Gọi tool
        tool_fn = AVAILABLE_TOOLS.get(tool_name)
        if not tool_fn:
            observation = f"LỖI: Tool '{tool_name}' không tồn tại. Tool hợp lệ: {list(AVAILABLE_TOOLS.keys())}"
        else:
            try:
                observation = tool_fn(*args)
            except Exception as e:
                observation = f"LỖI khi gọi tool: {str(e)}"

        action_str = f"{tool_name}[{', '.join(args)}]"
        print(f"🧠 Thought: {thought}")
        print(f"🛠️  Action: {action_str}")
        print(f"👁️  Observation: {observation}")

        trace_steps.append({
            "step": step,
            "thought": thought,
            "action": action_str,
            "observation": observation
        })

        history += f"\nThought: {thought}\nAction: {action_str}\nObservation: {observation}\n"

    if not final_answer:
        final_answer = "[Guardrail: đã đạt MAX_ITERATIONS, không có Final Answer]"
        print(f"🛡️ Guardrail kích hoạt: {final_answer}")

    return trace_steps, final_answer


TEST_CASES = [
    ("TC3", "Tôi là tien. Tính độ tương thích giữa tôi và hai giúp tôi."),
    ("TC4", "Tôi là tien. Xem hồ sơ của tôi, sau đó tìm giúp tôi những người có độ tương thích tối thiểu 60 điểm."),
    ("TC5", "Phân tích độ tương thích giữa cung 'Người Dơi' và kiểu tính cách MBTI 'XYZQ123' giúp tôi."),
]

all_results = {}
for label, question in TEST_CASES:
    steps, fa = run_react_trace(question, label)
    all_results[label] = {"question": question, "steps": steps, "final_answer": fa}

print("\n\n" + "="*60)
print("📊 TÓM TẮT TRACE LOG CHO trace_eval.md")
print("="*60)
for label, data in all_results.items():
    print(f"\n### {label}")
    print(f"Câu hỏi: {data['question']}")
    for s in data["steps"]:
        print(f"  Step {s['step']}:")
        print(f"    Thought: {s.get('thought','')}")
        if 'action' in s:
            print(f"    Action : {s['action']}")
            print(f"    Observation: {s['observation']}")
        if 'final_answer' in s:
            print(f"    Final Answer: {s['final_answer']}")
    print(f"  Final Answer: {data['final_answer']}")
