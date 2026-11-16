"""
演示
    LangChain Agent中有哪些tools
"""
from langchain_community.agent_toolkits.load_tools import get_all_tool_names

print(get_all_tool_names())