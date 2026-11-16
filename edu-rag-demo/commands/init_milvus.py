import typer
from clients.milvus import MilvusDBClient
from pymilvus import DataType
from config import config


# python cli.py init-milvus

def register(app):
    @app.command("init-milvus", help="初始化 milvus collection")
    def run():
        milvus = MilvusDBClient()
        create_collection(milvus)
        # 查询已有集合列表
        cols = milvus.list_collections()
        print(f"OK: 集合 `{config.MILVUS_COLLECTION_NAME}` 已就绪；当前库集合: {cols}")


def create_collection(milvus):
    name = config.MILVUS_COLLECTION_NAME
    if milvus.has_collection(name):

        milvus.client.drop_collection(name)
        print("集合已存在，已删除")

        # milvus.client.load_collection(name)
        # print(f"集合已存在，已加载: {name}")
        # return

    schema = milvus.client.create_schema(auto_id=True, enable_dynamic_field=True)
    schema.add_field("id", DataType.INT64, is_primary=True)
    schema.add_field("child_id", DataType.INT64)  # 用于检索的子块id
    schema.add_field("vector", DataType.FLOAT_VECTOR, dim=config.EMBEDDING_DIM)
    schema.add_field("parent_id", DataType.INT64)

    index_params = milvus.client.prepare_index_params()
    index_params.add_index(
        field_name="vector",
        index_name="vector_index",
        index_type="IVF_FLAT",
        metric_type="COSINE",
        params={"nlist": 128},
    )
    milvus.client.create_collection(
        collection_name=name, schema=schema, index_params=index_params
    )
    milvus.client.load_collection(name)
    print(f"已创建集合: {name}")
