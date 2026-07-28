"""Kiểm thử vòng lặp ReAct và Guardrail trong src/app.py — nhiệm vụ Role 1 ở
Mốc 3: "Kiểm tra xem Agent có vượt qua được câu bẫy Edge Case bằng phanh
Guardrail hay không".

Cố tình KHÔNG dùng MockProvider (vốn chỉ mô phỏng 5 test case chính thức một
cách "hợp tác"). Ở đây dùng các FakeProvider ĐỐI KHÁNG — cố tình lặp lại,
cố tình không bao giờ kết luận, cố tình gọi sai tool — để chứng minh cơ chế
Guardrail tự nó hoạt động đúng, không phụ thuộc vào việc model "may mắn"
trả lời hợp tác.

Chạy: python -m unittest discover -s tests -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import tools as tools_module  # noqa: E402
from app import run_react_agent  # noqa: E402
from prompts import GUARDRAIL_FALLBACK_MESSAGE, MAX_ITERATIONS  # noqa: E402


class ScriptedProvider:
    """Provider hợp tác: trả lời tuần tự theo kịch bản đã soạn sẵn."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = 0

    def generate(self, prompt, system_prompt=""):
        self.calls += 1
        index = min(self.calls - 1, len(self._responses) - 1)
        return self._responses[index]


class RepeatingProvider:
    """Provider "hỏng": luôn trả về ĐÚNG 1 Action giống hệt nhau mỗi lần —
    mô phỏng một LLM bị bí, cứ thử lại y hệt thay vì đổi chiến lược."""

    def __init__(self, action_line):
        self._action_line = action_line
        self.calls = 0

    def generate(self, prompt, system_prompt=""):
        self.calls += 1
        return self._action_line


class AlternatingNeverFinishingProvider:
    """Provider "hỏng": luôn đưa Action HỢP LỆ nhưng KHÁC nhau mỗi lần (né
    được guardrail lặp-action), và không bao giờ đưa Final Answer. Chỉ có
    MAX_ITERATIONS mới cắt được vòng lặp này."""

    _users = ["minh", "linh", "huy", "nga", "tuan", "lan", "thao", "hai"]

    def __init__(self):
        self.calls = 0

    def generate(self, prompt, system_prompt=""):
        user = self._users[self.calls % len(self._users)]
        self.calls += 1
        return f"Thought: kiểm tra {user}.\nAction: get_personality_profile['{user}']"


class MalformedProvider:
    """Provider "hỏng": không bao giờ theo đúng định dạng Thought/Action/Final Answer."""

    def __init__(self):
        self.calls = 0

    def generate(self, prompt, system_prompt=""):
        self.calls += 1
        return "Đây là câu trả lời tự do, không theo mẫu nào cả."


class TestReActLoopHappyPath(unittest.TestCase):

    def test_single_tool_call_then_final_answer(self):
        provider = ScriptedProvider([
            "Thought: cần xem hồ sơ tien.\nAction: get_personality_profile['tien']",
            "Thought: đã có dữ liệu.\nFinal Answer: Tien là nam 25 tuổi.",
        ])
        result = run_react_agent("Cho tôi biết về tien", provider)
        self.assertEqual(result["stopped_reason"], "final_answer")
        self.assertIn("Tien", result["answer"])
        self.assertEqual(provider.calls, 2)

    def test_no_tool_needed_direct_final_answer(self):
        provider = ScriptedProvider([
            "Thought: không cần tool.\nFinal Answer: Đây là câu trả lời lý thuyết.",
        ])
        result = run_react_agent("MBTI là gì?", provider)
        self.assertEqual(result["stopped_reason"], "final_answer")
        self.assertEqual(provider.calls, 1)

    def test_multi_tool_chain_accumulates_real_observations(self):
        provider = ScriptedProvider([
            "Thought: xem hồ sơ tien.\nAction: get_personality_profile['tien']",
            "Thought: tìm người phù hợp.\nAction: search_matches['tien', 60]",
            "Thought: đã đủ dữ liệu.\nFinal Answer: hai là người phù hợp nhất.",
        ])
        result = run_react_agent("Xem hồ sơ tien rồi tìm người phù hợp", provider)
        self.assertEqual(result["stopped_reason"], "final_answer")
        self.assertEqual(provider.calls, 3)
        actions = [s["action"] for s in result["steps"] if s["type"] == "action"]
        self.assertEqual(actions, ["get_personality_profile", "search_matches"])
        # Observation phải là dữ liệu THẬT lấy từ tool, không phải chuỗi rỗng.
        self.assertIn("Tien", result["steps"][0]["observation"])

    def test_unknown_user_error_is_surfaced_not_crashed(self):
        provider = ScriptedProvider([
            "Thought: tra cứu abc.\nAction: get_personality_profile['abc']",
            "Thought: không tìm thấy.\nFinal Answer: Không tìm thấy người dùng abc.",
        ])
        result = run_react_agent("Cho tôi biết về abc", provider)
        self.assertEqual(result["stopped_reason"], "final_answer")
        self.assertIn("LỖI", result["steps"][0]["observation"])


class TestGuardrails(unittest.TestCase):
    """Đây là phần kiểm chứng trực tiếp cho nhiệm vụ Role 1 ở Mốc 3."""

    def test_unknown_tool_name_does_not_crash(self):
        provider = ScriptedProvider([
            "Thought: gọi tool không tồn tại.\nAction: hack_the_planet['x']",
            "Thought: tool lỗi.\nFinal Answer: Không thể thực hiện yêu cầu này.",
        ])
        result = run_react_agent("Làm gì đó lạ", provider)
        self.assertEqual(result["stopped_reason"], "final_answer")
        self.assertIn("Không tìm thấy tool", result["steps"][0]["observation"])

    def test_repeated_identical_action_triggers_early_guardrail(self):
        provider = RepeatingProvider(
            "Thought: thử lại.\nAction: get_personality_profile['minh']"
        )
        result = run_react_agent("Cho tôi biết về minh", provider)
        self.assertEqual(result["stopped_reason"], "repeated_action")
        self.assertEqual(result["answer"], GUARDRAIL_FALLBACK_MESSAGE)
        # Guardrail phải dừng SỚM (ngay khi phát hiện lặp), không chờ hết MAX_ITERATIONS.
        self.assertLess(provider.calls, MAX_ITERATIONS + 1)

    def test_never_finishing_agent_is_cut_at_max_iterations(self):
        provider = AlternatingNeverFinishingProvider()
        result = run_react_agent("Tìm hiểu nhiều người giúp tôi", provider)
        self.assertEqual(result["stopped_reason"], "max_iterations")
        self.assertEqual(result["answer"], GUARDRAIL_FALLBACK_MESSAGE)
        self.assertEqual(provider.calls, MAX_ITERATIONS)

    def test_malformed_output_counts_toward_max_iterations_not_infinite(self):
        provider = MalformedProvider()
        result = run_react_agent("Câu hỏi bất kỳ", provider)
        self.assertEqual(result["stopped_reason"], "max_iterations")
        self.assertLessEqual(provider.calls, MAX_ITERATIONS)

    def test_tool_crash_is_caught_not_propagated(self):
        """Mô phỏng 1 tool tự crash (ném exception) thay vì trả chuỗi lỗi —
        xác nhận _call_tool của vòng lặp bắt được, không làm sập cả Agent."""
        original = tools_module.AVAILABLE_TOOLS["get_personality_profile"]

        def boom(user_id):
            raise RuntimeError("simulated crash")

        tools_module.AVAILABLE_TOOLS["get_personality_profile"] = boom
        try:
            provider = ScriptedProvider([
                "Thought: gọi tool sẽ crash.\nAction: get_personality_profile['minh']",
                "Thought: có lỗi.\nFinal Answer: Đã xảy ra lỗi khi tra cứu.",
            ])
            result = run_react_agent("Cho tôi biết về minh", provider)
            self.assertEqual(result["stopped_reason"], "final_answer")
            self.assertIn("LỖI", result["steps"][0]["observation"])
        finally:
            tools_module.AVAILABLE_TOOLS["get_personality_profile"] = original

    def test_real_tool_crash_from_wrong_arg_type_is_caught(self):
        """calculate_compatibility() thật sẽ crash nếu nhận tham số không
        phải string (gọi .lower() trên int) — xác nhận guardrail của vòng
        lặp cứu được lỗi THẬT từ tools.py, không chỉ lỗi giả lập."""
        provider = ScriptedProvider([
            "Thought: gọi với tham số sai kiểu.\nAction: calculate_compatibility[123, 'linh']",
            "Thought: có lỗi xảy ra.\nFinal Answer: Đã có lỗi khi tính toán.",
        ])
        result = run_react_agent("câu hỏi", provider)
        self.assertEqual(result["stopped_reason"], "final_answer")
        self.assertIn("LỖI", result["steps"][0]["observation"])

    def test_final_answer_before_action_in_same_response_is_respected(self):
        """Nếu model lẫn lộn, đưa cả Final Answer lẫn Action trong 1 phản hồi,
        agent phải tôn trọng thứ tự xuất hiện trong văn bản (Final Answer
        đứng trước -> dừng ngay, không cố gọi thêm Action phía sau)."""
        provider = ScriptedProvider([
            "Thought: xong rồi.\nFinal Answer: Kết luận cuối cùng.\n"
            "Action: get_personality_profile['minh']"
        ])
        result = run_react_agent("Câu hỏi", provider)
        self.assertEqual(result["stopped_reason"], "final_answer")
        self.assertEqual(provider.calls, 1)


class TestOfficialEdgeCaseTrap(unittest.TestCase):
    """Chạy đúng kịch bản bẫy của test case #5 (config/test_cases.json) qua
    một provider đối kháng cố tình không bao giờ chịu dừng, để chứng minh
    Guardrail vẫn thắng thế kể cả khi model không "hợp tác" như MockProvider."""

    def test_invalid_zodiac_and_mbti_trap_never_hallucinates_a_score(self):
        class StubbornInvalidRetryProvider:
            """Cứ đổi cách viết tên cung/MBTI không hợp lệ, không bao giờ bỏ cuộc."""

            def __init__(self):
                self.calls = 0

            def generate(self, prompt, system_prompt=""):
                self.calls += 1
                # Mỗi lần đổi 1 chút để né guardrail lặp-action, nhưng luôn
                # là một biến thể KHÔNG hợp lệ khác của cùng ý tưởng.
                return (
                    f"Thought: thử biến thể {self.calls}.\n"
                    f"Action: get_zodiac_compatibility['Người Dơi {self.calls}', 'Bọ Cạp']"
                )

        provider = StubbornInvalidRetryProvider()
        question = "Phân tích độ tương thích giữa cung 'Người Dơi' và kiểu tính cách MBTI 'XYZQ123' giúp tôi."
        result = run_react_agent(question, provider)

        # Agent không được crash và không được tự bịa một điểm số nào.
        self.assertEqual(result["stopped_reason"], "max_iterations")
        self.assertEqual(result["answer"], GUARDRAIL_FALLBACK_MESSAGE)
        self.assertNotRegex(result["answer"], r"\d+/100")
        for entry in result["steps"]:
            if entry["type"] == "action":
                self.assertIn("khong hop le", entry["observation"].lower().replace("ô", "o"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
