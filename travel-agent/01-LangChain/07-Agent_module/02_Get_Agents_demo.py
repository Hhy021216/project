"""
演示
    LangChain中Agent模块的使用
工作流程：
    1. 创建OpenAI模型对象
    2. 创建MemorySaver对象作为记忆存储
    3. 创建Agent对象，传入模型、工具和记忆存储器
    4. 调用Agent进行对话，Agent会根据用户输入调用工具
"""

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain.agents import create_agent
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv(r"D:\LangChain_project_gz8\03-code\01-LangChain\01-Models_module\.env")

# 1.创建OpenAI模型对象
model = ChatOpenAI(
    model="qwen-plus",
    temperature=0,
    max_tokens=1000,
    base_url=os.environ.get('base_url','https://dashscope.aliyuncs.com/compatible-mode/v1'),
    api_key=os.environ.get('DASHSCOPE_API_KEY'),
)

# 2.创建MemorySaver对象作为记忆存储
memory = MemorySaver()
tools = load_tools(['wikipedia', 'llm-math'], llm=model)

# 3.创建Agent对象
agent = create_agent(
    model=model,    # 使用的底层大模型
    tools=tools,   # 工具列表，这里包含了Wikipedia和LLM-Math工具，Agent可以调用这些工具来获取信息和进行计算
    checkpointer=memory,  # 传入上面的内存保存器，赋予Agent记忆能力
)

# 4.调用Agent进行对话
config = {
    "configurable": {"thread_id": "123456"}
}
for chunk in agent.stream(
        {"messages": [HumanMessage(content="计算一下300的25%是多少？")]},
        config
):
    print(chunk)
    print("----")

for chunk in agent.stream(
        {"messages": [HumanMessage(content="法国首都是哪里？")]},
        config
):
    print(chunk)
    print("----")