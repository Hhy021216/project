"""
演示
    使用LangGraph实现一个简单的短期记忆模块，能够在对话中记住用户的输入，并在后续对话中使用这些信息。
涉及到的API:
    create_agent
    InMemorySaver   # LangGraph的内存保存器，用于在对话过程中保存和恢复状态（记忆）
"""
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.messages import HumanMessage
from langchain_ollama import OllamaLLM
import time

# 1.创建Ollama模型对象
model = OllamaLLM(model="wangshenzhi/llama3-8b-chinese-chat-ollama-q4:v1")

# 2.创建InMemorySaver对象作为记忆存储
# 这是LangGraph的核心概念，用于在对话过程中保存和恢复状态（记忆）
checkpointer = InMemorySaver()

# 3.定义Agent配置
# thread_id: 线程ID，相当于对话ID，用于区分不同的对话
# 使用时间戳作为线程ID，确保每次运行都是一个新的线程ID
timestamp = int(time.time())
config1 = {
    "configurable": {"thread_id": timestamp},
}

# 4.创建Agent对象
agent = create_agent(
    model=model,    # 使用的底层大模型
    tools=[],   # 工具列表，这里为空，表示Agent只进行对话，不能调用外部工具（如搜索、计算器等）
    checkpointer=checkpointer,  # 传入上面的内存保存器，赋予Agent记忆能力
    system_prompt="你是一个通用助手。",  # 系统提示，定义Agent的角色和行为
)

# 5.第一轮对话，用户输入一句话，Agent进行回复
input1 = {
    "messages": [HumanMessage("你好，我十分喜欢猪脚饭。")]
}
# 调用Agent进行对话
response_a = agent.invoke(
    input=input1,
    config=config1
)
print(f"第一轮对话结果: {response_a}")

# 6.第二轮对话，用户输入另一句话，Agent进行回复
input2 = {
    "messages": [HumanMessage("我十分喜欢什么？")]
}
# 创建新的Agent配置
timestamp = int(time.time())
config2 = {
    "configurable": {"thread_id": timestamp}
}
# 调用Agent进行对话，Agent会根据之前保存的记忆进行回复
response_b = agent.invoke(
    input=input2,
    config=config2, # 使用新的配置,新的线程ID,确保和第一轮对话无关
)
print(f"第二轮对话结果: {response_b}")

# 使用相同的线程ID调用Agent，Agent会从记忆中恢复之前的对话状态，并进行回复
response_c = agent.invoke(
    input=input2,
    config=config1, # 使用第一轮的配置,相同的线程ID,确保和第一轮对话相关
)
print(f"第三轮对话结果: {response_c}")