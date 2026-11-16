"""LLM：OpenAI 兼容 API。"""
from openai import OpenAI
from config import config

class LLMClient:
    def __init__(self):
        api_key = config.OPENAI_API_KEY
        if not api_key or "请填写" in api_key or api_key.startswith("your-"):
            raise ValueError("请配置 OPENAI_API_KEY")
        base_url = config.OPENAI_BASE_URL
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = config.LLM_MODEL

    def chat(self, messages, temperature=0.1):
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                timeout=60,
            )
            return (resp.choices[0].message.content or "").strip()
        except Exception as e:
            print(f"LLM 调用失败: {e}")
            return f"抱歉，模型调用失败：{e}"

    def chat_stream(self, messages, temperature=0.1):
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                timeout=60,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            print(f"LLM 流式调用失败: {e}")
            yield f"抱歉，模型调用失败：{e}"