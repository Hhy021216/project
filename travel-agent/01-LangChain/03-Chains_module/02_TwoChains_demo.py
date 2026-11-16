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
model = OllamaLLM(model="wangshenzhi/llama3-8b-chinese-chat-ollama-q4:v1")
# 2.定义PromptTemplate提示词模板
template = "请给我讲个关于{name}的笑话吧"
prompt = PromptTemplate(
    input_variables=["name"],
    template=template)
# 3.创建第一条Chain链
chain01 = prompt | model
# 4.执行Chain链
result = chain01.invoke(input="鞋子")
print(result)
print("*"*50)
# 5.创建第二条Chain链
prompt02 = PromptTemplate(
    input_variables=["joke"],
    template="帮我优化这个笑话：{joke}，使它更有趣一些，面向儿童"
)
chain02 = prompt02 | model
# 6.连接两条Chain链
# all_chain = chain01 | chain02
all_chain = prompt | model | prompt02 | model
# 7.执行连接后的Chain链
result1 = all_chain.invoke(input="鞋子")
print(result1)