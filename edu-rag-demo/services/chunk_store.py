"""rag_chunk：父块写入（去重）。"""
from langchain_core.documents import Document
from db.models import RagChunk
from db.session import SessionLocal
from logger import logger
from langchain_text_splitters import RecursiveCharacterTextSplitter
from clients.embedding import EmbeddingClient
from clients.milvus import MilvusDBClient
from config import config
from db.models import RagChildChunk
from pathlib import Path



class ChunkStore:

    def __init__(self):
        self.embedding = EmbeddingClient()
        self.milvus = MilvusDBClient()

    def add_chunks(self, parents: list[Document]) -> list[Document]:
        """父块写入 MySQL，回填 id。"""
        if not parents:
            return []
        with SessionLocal() as session:
            for doc in parents:
                doc_file_name = doc.metadata.get("file_name") or ""
                doc_index = int(doc.metadata.get("index", 0))

                # 先做查询，不存在才插入
                row = (
                    session.query(RagChunk)
                    .filter(
                        RagChunk.doc_file_name == doc_file_name,
                        RagChunk.doc_index == doc_index,
                        RagChunk.content == doc.page_content
                    )
                    .first()
                )

                if not row:
                    row = RagChunk(
                        doc_file_name=doc_file_name,
                        doc_index=doc_index,
                        content=doc.page_content,
                    )
                    session.add(row)
                    session.flush()
                    # 入库后回填id，子块需要按id建立关联
                    doc.metadata["id"] = row.id

                    # 传入父块，切分子块
                    self.add_child_chunks(doc)

            session.commit()
            logger.info(f"父块写入 {len(parents)} 条 → rag_chunk")
            return parents


    def add_child_chunks(self, parent):
        """按 parent 先清旧子块，再：拆分 → MySQL → Milvus。不向外返回明细。"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHILD_CHUNK_SIZE,
            chunk_overlap=config.CHILD_CHUNK_OVERLAP,
            separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""],
        )

        with SessionLocal() as session:
            suffix = Path(parent.metadata["file_name"]).suffix.lower()
            if suffix == ".csv":
                child_texts = [parent.page_content]
            else:
                child_texts = splitter.split_text(parent.page_content)

            if not child_texts:
                return 

            parent_id = int(parent.metadata["id"])

            # 先清该父下旧子块，避免重复入库堆叠
            session.query(RagChildChunk).filter(
                RagChildChunk.parent_id == parent_id
            ).delete(synchronize_session=False)

            self.milvus.client.delete(
                collection_name=config.MILVUS_COLLECTION_NAME,
                filter=f"parent_id == {parent_id}",
            )

            # 子块入库，并得到子块 id
            rows = []
            for text in child_texts:
                row = RagChildChunk(
                    parent_id=parent_id,
                    content=text,
                )
                session.add(row)
                rows.append(row)
            session.flush()

            # 子块向量化，并写入 Milvus
            vectors = self.embedding.embed([r.content for r in rows])
            data = [
                {
                    "child_id": int(row.id),
                    "vector": vector,
                    "parent_id": parent_id,
                }
                for row, vector in zip(rows, vectors)
            ]
            self.milvus.client.insert(
                collection_name=config.MILVUS_COLLECTION_NAME,
                data=data,
            )

            # 当前父块处理完之后，就提交，如果写在上一层，所有父块都处理完才会提交
            session.commit()
