from logger import logger
from services.faq import FaqService
from services.greeting import match_greeting
from services.rag import RAGService
from services.web_search import WebSearchService
from services.fallback import FallbackService
import time


class QAPipeline:
    def __init__(self):
        self.faq_service = FaqService()
        self.rag_service = RAGService()
        self.web_search_service = WebSearchService()
        self.fallback_service = FallbackService()

    def query(self, question):
        question = (question or "").strip()
        logger.info(f"查询: {question!r}")

        # 打招呼
        answer = match_greeting(question)
        if answer:
            time.sleep(0.5)
            return {"answer": answer, "stage": "greeting", "score": 1.0}

        # faq环节
        answer, score = self.faq_service.search(question)
        if answer:
            time.sleep(0.5)
            return {"answer": answer, "stage": "faq", "score": score}

        # rag环节
        rows, score = self.rag_service.retrieve(question)
        if rows:
            answer = self.rag_service.generate(question, rows)
            return {"answer": answer, "stage": "rag", "score": score}

        # 联网环节
        answer = self.web_search_service.generate(question)
        if answer:
            return {"answer": answer, "stage": "web", "score": 1.0}

        # fallback兜底
        answer = self.fallback_service.answer(question)
        if answer:
            return {"answer": answer, "stage": "fallback", "score": 1.0}

        return {"answer": "没有命中任何策略，请稍后重试。", "stage": "miss", "score": 1.0}