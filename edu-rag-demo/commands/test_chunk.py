from pathlib import Path

import typer
from config import PROJECT_ROOT
from utils.chunking import load_and_chunk


def register(app):
    @app.command("test-chunk", help="解析切分单个知识库文件")
    def run(file_name=typer.Option(None, "--file_name", help="文件名称")):
        path = Path(file_name)
        if not path.is_absolute():
            path = PROJECT_ROOT / "storage" / "data" / path
        if not path.exists():
            raise SystemExit(f"文件不存在: {path}")


        docs = load_and_chunk(path)
        print(len(docs))



        # # 第一类先测 md/txt
        # docs = load_text_and_chunk(path)
        # print(len(docs))
        # print(docs[0])

        # 第二类，测试csv文件
        # docs = load_csv_and_chunk(path)
        # print(len(docs))
        # print(docs[0])

        # # 第三类，测试pdf文件
        # docs = load_file_and_chunk(path)
        # print(len(docs))
        # print(docs[0])


