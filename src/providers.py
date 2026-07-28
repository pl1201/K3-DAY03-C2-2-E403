"""
🔌 MULTI-PROVIDER LLM ADAPTER (OpenAI, Gemini, Anthropic, OpenRouter & Offline Mock)
Hỗ trợ chuyển đổi linh hoạt giữa các nhà cung cấp AI chỉ bằng cách đổi biến môi trường LLM_PROVIDER.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

class BaseLLMProvider:
    """Interface cơ sở cho tất cả các LLM Provider"""
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError


class GeminiProvider(BaseLLMProvider):
    """Google Gemini Provider"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gemini-2.5-flash"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            return "[Gemini Error]: Chưa cấu hình GEMINI_API_KEY trong file .env!"
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = client.models.generate_content(
                model=self.model_name,
                contents=contents
            )
            return response.text
        except Exception as e:
            return f"[Gemini Exception]: {str(e)}"


class OpenAIProvider(BaseLLMProvider):
    """OpenAI Provider (GPT-4o, GPT-3.5-turbo, etc.)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gpt-4o-mini"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            return "[OpenAI Error]: Chưa cấu hình OPENAI_API_KEY trong file .env!"
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[OpenAI Exception]: {str(e)}"


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude Provider (Claude 3.5 Sonnet, Claude 3 Haiku)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "claude-3-haiku-20240307"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_anthropic_api_key_here":
            return "[Anthropic Error]: Chưa cấu hình ANTHROPIC_API_KEY trong file .env!"
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            kwargs = {
                "model": self.model_name,
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            }
            if system_prompt:
                kwargs["system"] = system_prompt
                
            response = client.messages.create(**kwargs)
            return response.content[0].text
        except Exception as e:
            return f"[Anthropic Exception]: {str(e)}"


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter Provider (Hỗ trợ gọi mọi model qua OpenRouter API)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "google/gemini-2.5-flash"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openrouter_api_key_here":
            return "[OpenRouter Error]: Chưa cấu hình OPENROUTER_API_KEY trong file .env!"
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model_name,
                "messages": messages
            }
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"]
            else:
                return f"[OpenRouter API Error {res.status_code}]: {res.text}"
        except Exception as e:
            return f"[OpenRouter Exception]: {str(e)}"


class MockProvider(BaseLLMProvider):
    """Offline Mock Provider (Cho bài test không cần kết nối API).

    CHỈ mô phỏng kịch bản cho 5 test case chính thức trong
    config/test_cases.json, để demo được vòng lặp ReAct thật trong app.py
    khi không có API key. Đây KHÔNG phải NLU thật — nếu câu hỏi lệch khỏi
    5 kịch bản này, provider sẽ trả lời chung chung (không gọi tool) thay vì
    đoán mò. `prompt` mỗi lần gọi chứa TOÀN BỘ scratchpad tích luỹ (câu hỏi
    gốc + mọi Observation trước đó), nên có thể đếm số 'Observation:' để biết
    đang ở bước nào trong chuỗi nhiều-tool.
    """
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        # system_prompt phân biệt Chatbot Baseline (không có Action/Tool) với
        # ReAct Agent (bắt buộc định dạng Thought/Action/Final Answer). Nếu
        # gọi ở chế độ baseline, KHÔNG được trả về cú pháp ReAct — người dùng
        # sẽ thấy nguyên văn "Thought:.../Action:..." rất xấu và sai bản chất
        # (baseline không có Tool nên không nên nhắc tới Action).
        if "ReAct Agent" not in system_prompt:
            return (
                "(Mock) Mình chưa có kết nối API thật nên chỉ trả lời được "
                "bằng kiến thức lý thuyết chung, không tra cứu được dữ liệu "
                "thực tế cho câu hỏi này."
            )

        text = prompt.lower()
        observation_count = prompt.count("Observation:")

        # Test case 3: "Tôi là tien. Tính độ tương thích giữa tôi và hai..."
        if "tien" in text and "hai" in text and "tương thích" in text and observation_count == 0:
            return (
                "Thought: Cần tính độ tương thích giữa tien và hai.\n"
                "Action: calculate_compatibility['tien', 'hai']"
            )

        # Test case 4, bước 1: "Xem hồ sơ của tôi, sau đó tìm giúp tôi..."
        if "xem hồ sơ" in text and "tien" in text and observation_count == 0:
            return (
                "Thought: Cần xem hồ sơ của tien trước.\n"
                "Action: get_personality_profile['tien']"
            )
        # Test case 4, bước 2: đã có hồ sơ, giờ tìm ứng viên.
        if "tim" in text.replace("tìm", "tim") or "tìm" in text:
            if "tien" in text and observation_count == 1:
                return (
                    "Thought: Đã có hồ sơ, giờ tìm người phù hợp từ 60 điểm trở lên.\n"
                    "Action: search_matches['tien', 60]"
                )

        # Test case 5 (bẫy Guardrail): cung/MBTI không hợp lệ.
        if "người dơi" in text and observation_count == 0:
            return (
                "Thought: Cần kiểm tra độ hợp của cung 'Người Dơi'.\n"
                "Action: get_zodiac_compatibility['Người Dơi', 'Bọ Cạp']"
            )
        if "người dơi" in text and observation_count == 1:
            return (
                "Thought: Cung không hợp lệ, thử kiểm tra MBTI XYZQ123.\n"
                "Action: get_mbti_compatibility['XYZQ123', 'INTJ']"
            )
        if "người dơi" in text and observation_count >= 2:
            return (
                "Thought: Cả hai tool đều báo dữ liệu không hợp lệ, không thể "
                "tính toán tiếp.\n"
                "Final Answer: Xin lỗi, 'Người Dơi' không phải cung hoàng đạo hợp "
                "lệ và 'XYZQ123' không phải mã MBTI hợp lệ, nên tôi không thể "
                "đưa ra điểm tương thích cho cặp này."
            )

        # Đã có ít nhất 1 Observation cho các kịch bản khác -> tổng hợp luôn.
        if observation_count >= 1:
            return (
                "Thought: Đã có đủ dữ liệu từ Observation ở trên.\n"
                "Final Answer: (Mock) Đã tổng hợp xong kết quả từ dữ liệu thật "
                "phía trên Observation, không bịa thêm thông tin."
            )

        # Test case 1-2 (và mọi câu hỏi lý thuyết khác): không cần tool.
        return (
            "Thought: Câu hỏi này là kiến thức chung, không cần tra cứu dữ liệu.\n"
            "Final Answer: (Mock) Đây là câu trả lời từ kiến thức có sẵn, không "
            "cần gọi tool."
        )


def get_llm_provider(provider_name: str = None) -> BaseLLMProvider:
    """Factory function tự chọn Provider từ biến môi trường LLM_PROVIDER"""
    name = (provider_name or os.getenv("LLM_PROVIDER") or "mock").lower().strip()
    
    if name == "gemini":
        return GeminiProvider()
    elif name == "openai":
        return OpenAIProvider()
    elif name == "anthropic":
        return AnthropicProvider()
    elif name == "openrouter":
        return OpenRouterProvider()
    else:
        return MockProvider()


if __name__ == "__main__":
    print("=== TEST MULTI-PROVIDER LLM ADAPTER ===")
    provider = get_llm_provider()
    print(f"✅ Provider đang dùng: {provider.__class__.__name__}")
    print(f"🤖 User Query: Hello")
    print(f"💬 Response  : {provider.generate('Hello')}")
