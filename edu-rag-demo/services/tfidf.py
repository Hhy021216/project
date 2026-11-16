from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from logger import logger


class TfidfSearch:
    def __init__(self, tokenized_docs):
        # tokens 已是 jieba 结果，用空格拼接后按空格切开即可
        corpus = [" ".join(doc) for doc in tokenized_docs]
        self.vectorizer = TfidfVectorizer(analyzer=str.split)
        self.doc_vectors = self.vectorizer.fit_transform(corpus)
        logger.info(f"TfidfVectorizer 初始化完成，共 {len(tokenized_docs)} 条")

    def get_scores(self, tokenized_query):
        """返回查询与各文档的余弦相似度（0～1）。"""
        q = " ".join(tokenized_query)
        q_vec = self.vectorizer.transform([q])
        return cosine_similarity(q_vec, self.doc_vectors).ravel()
