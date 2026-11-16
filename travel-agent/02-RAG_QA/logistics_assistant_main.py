"""
演示
    一个简单的RAG问答系统-物流信息查询助手。
工作流程：
    1.离线部分：由知识库生成向量数据库。
    2.在线部分：用户输入问题，系统从向量数据库中检索相关文档，构造提示词，并结合大模型进行回答。
"""
import time
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

# 1.加载向量数据库
embed_model = OllamaEmbeddings(model="mxbai-embed-large")
vector_db = FAISS.load_local(
    "./faiss/logistics",
    embed_model,
    allow_dangerous_deserialization=True
)
start_time = time.time()

# 2.定义函数，将文档转为文本
def get_related_docs(related_docs):
    """
将相关文档列表转换为文本字符串，供提示词使用。
    """
    related_content = []
    for doc in related_docs:
        related_content.append(doc.page_content.replace("\n\n", "\n"))
    return "\n".join(related_content)

# 3.定义函数，构造提示词
def define_prompt():
    """
构造提示词，包含用户问题和相关文档内容。
    """
    question = '我的快递出发地是哪？预计几天的时间到达？'
    # 1.从向量数据库中检索相关文档
    docs = vector_db.similarity_search(question, k=2)
    # 2.将相关文档转换为文本
    related_content = get_related_docs(docs)
    # 3.构造提示词
    prompt_template = """
    基于已知信息，简洁专业的回答用户问题，不允许在答案中添加编造成分。
    已知信息为：
    {related_content}。
    用户问题为：
    {question}。
    """
    prompt = PromptTemplate(
        input_variables=["related_content", "question"],
        template=prompt_template,
    )
    prompt = prompt.format(related_content=related_content, question=question)
    return prompt

# 4.定义函数，调用大模型进行回答
def get_answer():
    prompt = define_prompt()
    model = OllamaLLM(model="qwen3:4b")
    print(f"构造的提示词: {prompt}")
    result = model.invoke(prompt)
    return result

# 主程序
if __name__ == '__main__':
    result = get_answer()
    print(f"答案: {result}")
    end_time = time.time()
    print(f"总耗时: {end_time - start_time:.4f}s")