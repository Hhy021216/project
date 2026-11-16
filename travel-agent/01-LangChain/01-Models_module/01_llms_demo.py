"""
演示
    调用大模型LLM的方法

涉及到的API:
    OllamaLLM

注意：
    目前企业中，多数使用ChatModel，比如ChatOpenAI，ChatOllama

"""

from langchain_ollama import OllamaLLM
# 1.实例化模型
model = OllamaLLM(model="wangshenzhi/llama3-8b-chinese-chat-ollama-q4:v1")
# 2.调用模型生成文本
result = model.invoke("请给我讲个笑话吧")
print(result)