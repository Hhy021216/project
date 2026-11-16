"""
演示
    PydanticOutputParser Pydantic表格解析器的使用
涉及到的API:
    PydanticOutputParser
    ChatPromptTemplate
    OllamaLLM
"""
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from pydantic import BaseModel, Field
from typing import List

# 1.实例化模型
model = OllamaLLM(model="qwen3:4b")
# 2.创建Pydantic解析器
# 定义Pydantic模型
class Movie(BaseModel):
    title: str = Field(description="电影标题")
    director: str = Field(description="导演")
    year: int = Field(description="上映年份")
    genre: List[str] = Field(description="电影类型")
    score: float = Field(description="评分（1-10）")

parser = PydanticOutputParser(pydantic_object= Movie)
# 3.创建提示词模版
format_instructions = parser.get_format_instructions()
prompt_template = ChatPromptTemplate.from_template(
    "生成一部{genre}电影的信息。\n{format_instructions}")
# 4.创建简单链
print("未使用解析器：")
chain1 = prompt_template | model
# 5.调用链
result = chain1.invoke(
    input={
        "genre": "科幻",
        "format_instructions": format_instructions
    }
)
print(type(result))
print(f"result1->{result}")
print("*"*50)

# 5.添加Pydantic解析器
chain2 = prompt_template | model | parser
result = chain2.invoke(
    input={
        "genre": "科幻",
        "format_instructions": format_instructions
    }
)
print(type(result))
print(f"result2->{result}")