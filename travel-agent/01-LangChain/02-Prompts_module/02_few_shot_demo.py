"""
演示
    few_shot/少样本 提示词的用法
涉及到的API:
    PromptTemplate
    FewShotPromptTemplate
    OllamaLLM
"""
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_ollama import OllamaLLM

# 1.实例化模型
model = OllamaLLM(model="wangshenzhi/llama3-8b-chinese-chat-ollama-q4:v1")

# 2.定义few_shot提示词模板
examples = [
    {"word": "开心", "antonym": "难过"},
    {"word": "高", "antonym": "低"}
]

example_template = """
单词: {word}
反义词: {antonym}\\n
"""

example_prompt = PromptTemplate(
    input_variables=["word", "antonym"],
    template=example_template
)
# 3.使用提示词模板生成一个具体的提示词
prompt_template = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="给出每个单词的反义词",
    suffix="单词: {input}\\n反义词:",
    input_variables=["input"],
    example_separator="\\n"
)
prompt_text = prompt_template.format(input="大")
print(prompt_text)
# 4.提示词输入大模型
result = model.invoke(prompt_text)
print(result)