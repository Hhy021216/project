import typer
from logger import logger
from services.greeting import match_greeting
from services.faq import FaqService
from pipeline import QAPipeline


def register(app):
    @app.command("test-ask", help="对话流程测试脚本")
    def run(question=typer.Option(None, help="用户问题")):
        if not question or not str(question).strip():
            raise SystemExit('用法: python cli.py test-ask --question="你的问题"')

        pipeline = QAPipeline()
        result = pipeline.query(question)
        print(result)
