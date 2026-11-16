"""
演示
    Chain链的用法
涉及到的API:
    PromptTemplate
    OllamaLLM
    prompt | llm
"""
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

# 1.实例化模型
model = OllamaLLM(model="qwen3:4b")
# 2.定义PromptTemplate提示词模板
template = "请给我讲个关于{name}的笑话吧"
prompt = PromptTemplate(
    input_variables=["name"],
    template=template
)
# 3.创建一条Chain链
chain = prompt | model
# 4.执行Chain链
result = chain.invoke(input="鞋子")
print(result)
print("*"*50)