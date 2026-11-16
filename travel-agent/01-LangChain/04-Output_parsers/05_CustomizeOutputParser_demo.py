"""
演示
    CustomizeOutputParser 自定义解析器的使用
涉及到的API:
    BaseOutputParser
    ChatPromptTemplate
    OllamaLLM
"""
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from typing import Dict, Any

# 1.实例化模型
model = OllamaLLM(model="wangshenzhi/llama3-8b-chinese-chat-ollama-q4:v1")
# 2.创建自定义解析器
class CustomKeyValueParser(BaseOutputParser[Dict[str, Any]]):
    """自定义解析器，将输出解析为键值对格式"""
    def parse(self, text: str) -> Dict[str, Any]:
        """从文本中解析键值对"""
        result = {}
        lines = text.strip().split('\n')
        # 遍历行，解析键值对
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                result[key.strip()] = value.strip()
        return result
    def get_format_instructions(self) -> str:
        """说明模型输出格式"""
        return """请以'键: 值'的格式返回信息，每行一个键值对。
                例如：
                姓名: 张三
                职业: AI大模型工程师
                年龄: 30
                兴趣: 编程、泡脚
                技能: Python、Java、C++"""

parser = CustomKeyValueParser()
# 3.创建提示词模版
format_instructions = parser.get_format_instructions()
prompt_template = ChatPromptTemplate.from_template(
    "提供{person}的基本信息。\n{format_instructions}")
# 4.创建简单链
print("未使用解析器：")
chain1 = prompt_template | model
# 5.调用链
result = chain1.invoke(
    input={
        "person": "孙悟空",
        "format_instructions": format_instructions
    }
)
print(type(result))
print(f"result1->{result}")
print("*"*50)

# 6.添加自定义解析器
print("使用解析器：")
chain2 = prompt_template | model | parser
# 7.调用链
result = chain2.invoke(
    input={
        "person": "孙悟空",
        "format_instructions": format_instructions
    }
)
print(type(result))
print(f"result2->{result}")