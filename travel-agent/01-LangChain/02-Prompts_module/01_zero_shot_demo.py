"""
演示
    zero_shot/0样本 提示词的用法
涉及到的API:
    PromptTemplate
    OllamaLLM
"""
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

# 1.实例化模型
model = OllamaLLM(model="wangshenzhi/llama3-8b-chinese-chat-ollama-q4:v1")
# 2.定义zero_shot提示词模板
template = "我的邻居姓{lastname}，他生了个儿子，给他儿子起个名字"
prompt_template = PromptTemplate(
    input_variables=["lastname"],
    template=template
)
# 3.使用提示词模板生成一个具体的提示词
prompt_text = prompt_template.format(lastname="王")
print(prompt_text)
# 4.提示词输入大模型
result = model.invoke(prompt_text)
print(result)