"""
演示
    ChatPromptTemplate的用法
涉及到的API:
    ChatPromptTemplate
    OllamaLLM

"""
# 方法1.直接提问
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_ollama import OllamaLLM
#
# # 1.实例化模型
# model = OllamaLLM(model="wangshenzhi/llama3-8b-chinese-chat-ollama-q4:v1")
# # 2.定义ChatPromptTemplate提示词模板
# template_str = "帮我讲个关于{name}笑话吧"
# prompt_template = ChatPromptTemplate.from_template(template_str)
# prompt = prompt_template.format_messages(name="猪八戒")
# print(f'prompt->{prompt}')
# # 3.提示词输入大模型
# result = model.invoke(prompt)
# print(f'result->{type(result)}')
# print(f'result->{result}')

# 方法2.zero shot提问
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_ollama import OllamaLLM
from langchain_core.messages import SystemMessage, HumanMessage

# 1.实例化模型
model = OllamaLLM(model="wangshenzhi/llama3-8b-chinese-chat-ollama-q4:v1")
# 2.定义ChatPromptTemplate提示词模板
# 系统提示词
system_prompt = SystemMessage("你是取名专家。")
# 用户提示词模板
human_str = "我的邻居姓{lastname}，他生了个儿子，给他儿子起个名字"
human_template = HumanMessagePromptTemplate.from_template(human_str)
# 组装提示词模板
chat_template = ChatPromptTemplate.from_messages([system_prompt, human_template])
# 3.生成最终提示词
prompt = chat_template.format_messages(lastname="王")
print(f'prompt->{prompt}')
# 4.调用模型
result = model.invoke(prompt)
print(f'result->{result}')
#
# # 方法3.few shot提问
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_ollama import OllamaLLM
# from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
# # 1.实例化模型
# model = OllamaLLM(model="wangshenzhi/llama3-8b-chinese-chat-ollama-q4:v1")
# # 2.定义ChatPromptTemplate提示词模板
# prompt_template = ChatPromptTemplate.from_messages(
#      [
#          ("system", "给出每个单词的反义词"),
#          MessagesPlaceholder("history"),    # 位置保持, 用于存储历史对话
#          ("human", "{question}"),
#      ]
# )
# # 3.生成最终提示词
# # history = [
# #     ("human", "开心"),
# #     ("ai", "难过"),
# #     ("human", "高"),
# #     ("ai", "矮")
# # ]
# history = [
#     HumanMessage(content="开心"),
#     AIMessage(content="难过"),
#     HumanMessage(content="高"),
#     AIMessage(content="矮")
# ]
# prompt = prompt_template.format_messages(history=history, question="富有")
# print(f'prompt->{prompt}')
# # 4.调用模型
# result = model.invoke(prompt)
# print(f'result->{result}')