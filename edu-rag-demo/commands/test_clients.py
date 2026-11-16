import typer
from clients.llm import LLMClient
from clients.embedding import EmbeddingClient

def register(app):
    @app.command("test-clients", help="试连已接入的客户端")
    def test_clients():
        # messages = [
        #     {"role": "user", "content": "你是什么模型？"},
        # ]
        # print(LLMClient().chat(messages))

        cient = EmbeddingClient()
        print(len(cient.embed(["你好"])[0]))


