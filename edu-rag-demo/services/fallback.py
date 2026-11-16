from clients.llm import LLMClient
from config import config
from prompts import FALLBACK_PROMPT


class FallbackService:
    def __init__(self, llm=None):
        self.llm = llm or LLMClient()

    def answer(self, query):
        prompt = FALLBACK_PROMPT.format(
            phone=config.CUSTOMER_SERVICE_PHONE,
            question=query,
        )
        return self.llm.chat([{"role": "user", "content": prompt}])
