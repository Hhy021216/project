from config import config
from logger import logger
from clients.embedding import EmbeddingClient
from clients.milvus import MilvusDBClient
from clients.llm import LLMClient
from db.models import RagChunk
from db.session import SessionLocal
from prompts import RAG_PROMPT


class RAGService:
    def __init__(self):
        self.embedding = EmbeddingClient()
        self.milvus = MilvusDBClient()
        self.llm = LLMClient()

    def vector_search(self, question: str):
        vector = self.embedding.embed([question])[0]
        candidate_m = config.RETRIEVAL_K * 4

        results = self.milvus.client.search(
            collection_name=config.MILVUS_COLLECTION_NAME,
            data=[vector],
            anns_field="vector",  # 检索字段值
            search_params={
                "metric_type": "COSINE",
                "params": {
                    "nprobe": 10,  # Milvus 会把向量聚成 nlist 个簇，检索时只扫描离查询最近的nprobe簇。
                    "radius": config.RAG_SCORE_THRESHOLD,  # 半径 / 相似度阈值，只返回相似度 ≥ 该值的结果。
                },
            },
            limit=candidate_m,
            output_fields=["child_id", "parent_id"], # 只返回必要的字段，vector只在查询时有用，不返回这个向量值
        )[0]

        logger.info(f"子块召回（过阈值）{len(results)} 条")
        return results


    def retrieve(self, question):
        results = self.vector_search(question)

        if not results:
            return [], 0.0

        # 有序的结果
        ordered_results = {}

        for hit in results:
            entity = hit.get("entity")
            score = float(hit.get("distance", 0.0))
            parent_id = entity.get("parent_id")
            # 已按分数降序：同一 parent_id 只留第一次（最高分）
            if parent_id is None or parent_id in ordered_results:
                continue
            ordered_results[int(parent_id)] = score

        parent_ids = list(ordered_results.keys())[: config.RETRIEVAL_K]
        # print(parent_ids)

        # 拿着parent_ids去数据库中取父块，供后面的大模型生成使用
        # 但是，取到的数据，要和召回的相似度顺序一致
        with SessionLocal() as session:
            # in操作查询到的数据是无序的
            rows = (
                session.query(RagChunk)
                .filter(RagChunk.id.in_(parent_ids))
                .all()
            )
        by_id = {int(r.id): r for r in rows}

        # result = []
        # for pid in parent_ids:
        #     if pid in by_id:
        #         result.append(by_id[pid])

        ordered_rows = [by_id[pid] for pid in parent_ids if pid in by_id]
        # rag召回的数据中，最大的相似度分数
        best_score = ordered_results[parent_ids[0]]
        return ordered_rows, best_score


    def generate(self, question, rows):
        context = ""
        for row in rows:
            prefix = (
                f"\n===== 《{row.doc_file_name}》第{row.doc_index}段，内容如下： ======\n"
            )
            context += prefix + (row.content or "")

        prompt = RAG_PROMPT.format(context=context, question=question)
        return self.llm.chat([{"role": "user", "content": prompt}])


