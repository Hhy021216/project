import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent
load_dotenv(PROJECT_ROOT / ".env")


class Config:
    def __init__(self):
        self.MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
        self.MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
        self.MYSQL_USER = os.getenv("MYSQL_USER", "root")
        self.MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "123456")
        self.MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "edu_rag")

        self.MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
        self.MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
        self.MILVUS_DATABASE_NAME = os.getenv("MILVUS_DATABASE_NAME", "default")
        self.MILVUS_COLLECTION_NAME = os.getenv("MILVUS_COLLECTION_NAME", "default")
        self.EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "1024"))

        self.TFIDF_THRESHOLD = float(os.getenv("TFIDF_THRESHOLD", "0.5"))

        self.CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
        self.CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

        self.CHILD_CHUNK_SIZE = int(os.getenv("CHILD_CHUNK_SIZE", "200"))
        self.CHILD_CHUNK_OVERLAP = int(os.getenv("CHILD_CHUNK_OVERLAP", "20"))

        self.RETRIEVAL_K = int(os.getenv("RETRIEVAL_K", "5"))
        self.RAG_SCORE_THRESHOLD = float(os.getenv("RAG_SCORE_THRESHOLD", "0.5"))

        self.SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")
        self.WEB_SEARCH_MAX_RESULTS = int(os.getenv("WEB_SEARCH_MAX_RESULTS", "5"))

        self.CUSTOMER_SERVICE_PHONE = os.getenv("CUSTOMER_SERVICE_PHONE", "400-618-4000")


        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        self.OPENAI_BASE_URL = os.getenv(
            "OPENAI_BASE_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.LLM_MODEL = os.getenv("LLM_MODEL", "qwen-plus")

        self.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-v3")

        log_file = os.getenv("LOG_FILE", "storage/logs/app.log")
        self.LOG_FILE = str(
            Path(log_file) if Path(log_file).is_absolute() else PROJECT_ROOT / log_file
        )


    @property 
    def DATABASE_URL(self):
        """SQLAlchemy / Alembic 共用的连接串。"""
        user = quote_plus(self.MYSQL_USER)
        password = quote_plus(self.MYSQL_PASSWORD)
        return (
            f"mysql+pymysql://{user}:{password}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            f"?charset=utf8mb4"
        )


config = Config()

