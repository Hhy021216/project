"""Milvus 连接客户端。"""
from pymilvus import MilvusClient
from config import config

class MilvusDBClient:
    def __init__(self):
        host = config.MILVUS_HOST
        port = config.MILVUS_PORT
        database = config.MILVUS_DATABASE_NAME
        self.uri = f"http://{host}:{port}"
        self.database = database
        self.client = MilvusClient(uri=self.uri, db_name=database)
        print(f"Milvus 连接成功: {self.uri} db={database}")

    def list_collections(self):
        return self.client.list_collections()

    def has_collection(self, name):
        return self.client.has_collection(name)