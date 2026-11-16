import json

import numpy as np

from config import config
from db.models import Faq
from db.session import SessionLocal
from logger import logger
from services.tfidf import TfidfSearch
from utils.preprocess import preprocess_text


class FaqService:
    def __init__(self):
        self.ids = []
        self.questions = []
        self.answers = []
        self.tfidf = None
        self._reload()

    def _reload(self):
        """从 MySQL 读取问答 + tokens，建 TF-IDF。"""
        with SessionLocal() as session:
            db_rows = session.query(Faq).all()

        self.ids = []
        self.questions = []
        self.answers = []
        tokenized = []

        for row in db_rows:
            # tokens 为空的情况可能有哪些？
            if not row.tokens:
                continue

            try:
                tokens = json.loads(row.tokens)
            except Exception:
                logger.warning(f"FAQ id={row.id} tokens 解析失败，已跳过")
                continue
            if not tokens:
                continue

            self.ids.append(row.id)
            self.questions.append(row.question)
            self.answers.append(row.answer)
            tokenized.append(tokens)

        if not tokenized:
            self.tfidf = None
            logger.warning("MySQL 无可用 FAQ 分词，请先执行: python cli.py ingest-faq")
            return

        self.tfidf = TfidfSearch(tokenized)
        logger.info(f"FAQ 索引加载完成：{len(self.ids)} 条（MySQL 问答 + tokens）")


    def search(self, query, threshold=None):
        """命中返回 (answer, score)，未命中返回 (None, score)。"""
        threshold = config.TFIDF_THRESHOLD if threshold is None else threshold
        if not query or not self.tfidf:
            return None, 0.0

        scores = self.tfidf.get_scores(preprocess_text(query))
        if scores is None or len(scores) == 0:
            return None, 0.0

        # 相似度最高的数据对应的索引
        best_idx = int(np.argmax(scores))

        best_score = float(scores[best_idx])
        logger.info(f"TF-IDF 最高分={best_score:.3f} (阈值={threshold})")

        if best_score < threshold:
            return None, best_score

        return self.answers[best_idx], best_score
