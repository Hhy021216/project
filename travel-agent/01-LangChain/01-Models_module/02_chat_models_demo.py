"""
演示
    聊天模型 ChatModel 的调用方式
    invoke() 支持三种输入: 字符串、Message对象列表、字典列表
    推荐使用 Message 对象，这是 LangChain 的标准写法
涉及到的API:
    ChatOpenAI / ChatOllama
    SystemMessage / HumanMessage
"""
import os
from dotenv import load_dotenv
load_dotenv()

# ==============================
# 方法1: 使用 ChatOpenAI 调用云端模型 (qwen)
# ==============================
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# 1.实例化模型
model = ChatOpenAI(
    base_url=os.environ.get('base_url', "https://dashscope.aliyuncs.com/compatible-mode/v1"),
    model="qwen-plus",
    api_key=os.environ.get('DASHSCOPE_API_KEY'),
    temperature=0
)

# --- 方式A: 传入字符串（最简单，自动包装为 HumanMessage）---
print("=== 方式A: 字符串输入 ===")
result = model.invoke("你好，请介绍一下你自己")
print(result.content)
print("-" * 80)

# --- 方式B: 传入 Message 对象列表（推荐，可设置系统角色）---
print("=== 方式B: Message 对象输入（推荐）===")
messages = [
    SystemMessage(content="你是一个充满想象的诗人"),   # 系统提示词：设定角色
    HumanMessage(content="请给我写一首关于春天的唐诗") # 用户提示词：提出问题
]
result = model.invoke(messages)
print(result.content)
print("-" * 80)

# ==============================
# 方法2: 使用 ChatOllama 调用本地模型
# ==============================
# from langchain_ollama import ChatOllama
#
# # 1.实例化本地模型
# model = ChatOllama(model="qwen3:4b")
#
# # 2.定义 Message 列表
# messages = [
#     SystemMessage(content="你是一个充满想象的诗人"),
#     HumanMessage(content="请给我写一首关于春天的唐诗")
# ]
#
# # 3.调用模型
# result = model.invoke(messages)
# print(result.content)