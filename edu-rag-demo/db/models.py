from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from db.base import Base


class Faq(Base):
    __tablename__ = "faq"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(50), nullable=True)
    question = Column(String(1000), nullable=True)
    answer = Column(String(2000), nullable=True)
    tokens = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)


class RagChunk(Base):
    __tablename__ = "rag_chunk"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(Integer, nullable=True)  # 预留
    doc_file_name = Column(String(256), nullable=True)
    doc_index = Column(Integer, nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)


class RagChildChunk(Base):
    __tablename__ = "rag_child_chunk"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, nullable=False, index=True)  # → rag_chunk.id
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

