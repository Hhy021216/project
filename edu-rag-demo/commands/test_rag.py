import typer
from logger import logger
from services.rag import RAGService


def register(app):
    @app.command("test-rag", help="RAG 检索演示")
    def run(question=typer.Option(None, help="用户问题")):
        if not question or not str(question).strip():
            raise SystemExit('用法: python cli.py test-rag --question "你的问题"')

        print(question)

        rows, best_score = RAGService().retrieve(question)
        # logger.info(rows)

        result = RAGService().generate(question, rows)
        print(result)

