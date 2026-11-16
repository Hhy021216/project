"""
演示
    ChatMessageHistory 聊天记录的用法
涉及到的API:
    ChatMessageHistory
    messages_to_dict
    messages_from_dict
"""

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import messages_to_dict, messages_from_dict
import json

# 1.创建ChatMessageHistory聊天记录对象，用于存储聊天信息
history = ChatMessageHistory()
# 添加用户消息
history.add_user_message("在吗？")
# 添加大模型消息
history.add_ai_message("在")
print(f'history.messages-->{history.messages}')
# 2.将聊天信息保存为字典
# 将history.messages转换为字典
dicts = messages_to_dict(history.messages)
print(f'dicts-->{dicts}')
# 保存字典为JSON文件
with open("history.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(dicts, indent=2, ensure_ascii=False))

# 3.读取字典
messages = json.load(open("history.json", "r", encoding="utf-8"))
chat_messages = messages_from_dict(messages)
print(f'chat_messages-->{chat_messages}')