from pathlib import Path

import typer
from config import PROJECT_ROOT
from utils.chunking import load_and_chunk
from services.chunk_store import ChunkStore

def register(app):
    @app.command("ingest-rag", help="RAG 知识库入库")
    def run(file_name=typer.Option(None, "--file_name", help="文件名称")):
        path = Path(file_name)
        if not path.is_absolute():
            path = PROJECT_ROOT / "storage" / "data" / path
        if not path.exists():
            raise SystemExit(f"文件不存在: {path}")

        parent_texts = load_and_chunk(path)

        chunk_store = ChunkStore()
        parents = chunk_store.add_chunks(parent_texts)
        print('父块数量', len(parents))

        # chunk_store.add_child_chunks(parents)
        # print('子块写入成功')

