import typer
from logger import logger


# python cli.py demo
# python cli.py demo --qestion="你好"

def register(app):
    @app.command("demo", help="打印一行，验证 commands 是否接通")
    def demo(
        question=typer.Option(None, help="用户问题"),
    ):
        logger.warning("注意，可能有小问题")
        
        print("OK: commands 已连通，可以开始写业务命令了")
        if question:
            print("用户问题", question)
