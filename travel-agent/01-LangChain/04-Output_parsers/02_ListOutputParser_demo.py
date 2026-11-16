"""
演示
    CommaSeparatedListOutputParser 列表解析器的使用
涉及到的API:
    CommaSeparatedListOutputParser
    ChatPromptTemplate
    OllamaLLM
"""
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM

# 1.实例化模型
model = OllamaLLM(model="wangshenzhi/llama3-8b-chinese-chat-ollama-q4:v1")
# 2.创建列表解析器
parser = CommaSeparatedListOutputParser()
# 3.定义提示词模版
format_instructions = parser.get_format_instructions()
prompt_template = ChatPromptTemplate.from_template(
    "用中文列出{topic}的五个最重要特点？\n{format_instructions}")
# 4.创建链
print("未使用解析器：")
chain1 = prompt_template | model
# 5.调用链
result = chain1.invoke(
    input={
        "topic": "AI",
        "format_instructions": format_instructions
    }
)
print(type(result))
print(f"result->{result}")
print("*"*50)

# 6.添加列表解析器
print("使用列表解析器：")
chain2 = prompt_template | model | parser
# 7.调用链
result = chain2.invoke(
    input={
        "topic": "AI",
        "format_instructions": format_instructions
    }
)
print(type(result))
print(f"result->{result}")