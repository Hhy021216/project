"""
演示
    StrOutputParser 字符串解析器的用法
涉及到的API:
    StrOutputParser
    ChatPromptTemplate
    ChatOpenAI  # 这里使用ChatOpenAI调用qwen3.6-plus模型，返回的结果不是字符串，而是一个包含content属性的对象，需要使用StrOutputParser进行解析
    OllamaLLM  # 这里使用OllamaLLM调用qwen3:4b模型，返回的结果就是字符串，不需要解析
"""
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv  # 加载环境变量的库, 需要安装dotenv: pip install dotenv

# 0.加载环境变量，获取API密钥
load_dotenv(r"D:\LangChain_project_gz8\03-code\01-LangChain\01-Models_module\.env")
# 1.实例化模型
model = ChatOpenAI(
    base_url=os.environ.get('base_url',"https://dashscope.aliyuncs.com/compatible-mode/v1"),
    model="qwen-plus",
    api_key=os.environ.get('DASHSCOPE_API_KEY'),
    temperature=0.1
)

# 2.定义提示词模版
prompt_template = ChatPromptTemplate.from_template(
    "解释{topic}是什么？回答控制20字以内")
# 3.创建简单链
chain1 = prompt_template | model
result = chain1.invoke(input={"topic": "AI"})
print(f"result1-->{result}")
# 4.添加字符串解析器
parser = StrOutputParser()
chain2 = prompt_template | model | parser
result2= chain2.invoke(input={"topic": "AI"})
print(f"the type -->{type(result2)}")
print(f"result2-->{result2}")