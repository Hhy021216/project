"""
演示
    JsonOutputParser JSON解析器的使用
涉及到的API:
    JsonOutputParser
    ChatPromptTemplate
    OllamaLLM
"""
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM

# 1.实例化模型
model = OllamaLLM(model="wangshenzhi/llama3-8b-chinese-chat-ollama-q4:v1")
# 2.创建JSON解析器
parser = JsonOutputParser()
# 3.创建提示词模版
format_instructions = parser.get_format_instructions()
prompt_template = ChatPromptTemplate.from_template(
    "生成一个包含{person}基本信息。包括姓名、职业、年龄、兴趣和技能列表，不要包含任何额外内容。\n{format_instructions}")
# 4.创建简单链
print("未使用解析器：")
chain1 = prompt_template | model
# 5.调用链
result = chain1.invoke(
    input={
        "person": "猪八戒",
        "format_instructions": format_instructions
    }
)
print(type(result))
print(f"result1->{result}")
print("*"*50)

# # 6.添加JSON解析器
# print("使用JSON解析器：")
# chain2 = prompt_template | model | parser
# result = chain2.invoke(
#     input={
#         "person": "猪八戒",
#         "format_instructions": format_instructions
#     }
# )
# print(type(result))
# print(f"result2->{result}")