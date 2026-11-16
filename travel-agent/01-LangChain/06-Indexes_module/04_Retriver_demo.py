"""
演示
    Retriever 检索器的用法
    包括 Chroma, Milvus, FAISS, Redis
涉及的API:
    Chroma
    chroma_db.as_retriever
"""
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

#demo 1
# 1.创建向量数据库对象
embed_model = OllamaEmbeddings(model="mxbai-embed-large")
# 直接加载已经存在的向量数据库
chroma_db = Chroma(persist_directory="./chroma_db", embedding_function=embed_model)

# 2.查询向量数据库
query = "1937年北京大学发生了什么？"
# 使用similarity_search
# result = chroma_db.similarity_search(query, k=2)
# print(f'result->{result}')
# 使用as_retriever 方法返回 Retriever 对象，然后调用 invoke 方法进行查询
retriever = chroma_db.as_retriever(search_kwargs={"k":2})
result = retriever.invoke(query)
print(f'result->{result}')

#demo 2
# 2.拓展-BM25Retriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
# ======================================================================
# 2. BM25 关键词检索（生产环境最常用）
# ======================================================================
# 【原理】BM25 是经典关键词匹配算法，Elasticsearch 等搜索引擎底层都使用 BM25
#
#   核心公式（简化理解）：
#     文档得分 = Σ  词频权重(TF) × 稀有度权重(IDF)
#              查询中每个词
#
#     TF（词频）：这个词在文档中出现的次数越多，得分越高
#                 但有饱和机制——出现100次不比10次高多少，防止过度匹配
#     IDF（逆文档频率）：这个词在所有文档中越少见，权重越高
#                 "的""是"每篇都有 → IDF低 → 不重要
#                 "量子计算"很少出现 → IDF高 → 很重要
#
#   优点：速度快，精确匹配关键词，不需要GPU
#   缺点：不理解语义，"北大"无法匹配"北京大学"
# ======================================================================

# 1.构造要检索匹配的文档列表
docs = [
    Document(page_content="量子计算是一种基于量子力学的计算范式。"),
    Document(page_content="人工智能是模拟人类智能的技术。"),
    Document(page_content="风力发电是可再生能源。"),
    Document(page_content="太阳能是可再生能源。"),
    Document(page_content="具身智能技术是AI和机器人技术的交叉领域。"),
    Document(page_content="水力发电是可再生能源。"),
]

from langchain_community.retrievers import BM25Retriever
import jieba

# 2.构建BM25检索器
# 中文分词函数：BM25 按空格切分词语，中文没有空格，需要先分词
# 例如："量子计算是一种技术" → "量子 计算 是 一种 技术"
def preprocess_text(text):
    return " ".join(jieba.cut(text))

# 对文档进行预分词后传入 BM25
retriever = BM25Retriever.from_documents(
    documents=[Document(page_content=preprocess_text(doc.page_content)) for doc in docs],
)
retriever.k = 2

# 3.使用BM25检索器进行检索
# 查询也需要同样分词
query = "量子计算"
query = preprocess_text(query)
results = retriever.invoke(query)
print(f'\n=== BM25 检索结果（查询：{query}）===')
print(f"result->{results}")