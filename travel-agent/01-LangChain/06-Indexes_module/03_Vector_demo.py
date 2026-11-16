"""
演示
    VectorStores 向量数据库的用法
    包括 Chroma, Milvus, FAISS, Redis
涉及的API:
    Chroma

工作流:
    1.离线部分：
        加载文档 -> 文本分割 -> 嵌入模型 -> 创建嵌入向量 -> 存储到向量数据库
    2.在线部分:
        用户问题Query -> Query向量 -> 相似度检索 -> topK结果

"""
from langchain_community.document_loaders import TextLoader # 文档加载器
from langchain_text_splitters import CharacterTextSplitter # 字符文本分割器
from langchain_ollama import OllamaEmbeddings # 嵌入模型
from langchain_chroma import Chroma # 向量数据库

# 1.加载文本数据
loader = TextLoader("./data/pku.txt", encoding='utf-8')
docs = loader.load()
# print(f'docs->{docs}')

# 2.文本分割
text_splitter = CharacterTextSplitter(
    separator="\n\n",
    chunk_size=200, # 分割后块的最大长度
    chunk_overlap=20,  # 每个块之间的重叠长度
)
split_docs = text_splitter.split_documents(docs)
print(f'split_docs->{split_docs}')
print(f'len(split_docs)->{len(split_docs)}')

# 3.创建嵌入模型
embed_model = OllamaEmbeddings(model="mxbai-embed-large")

# 4.创建向量数据库
chroma_db = Chroma.from_documents(
    documents=split_docs, # Document列表
    embedding=embed_model, # 嵌入模型
    persist_directory="./chroma_db", # 持久化目录
)

# 直接加载已经存在的向量数据库
# chroma_db = Chroma(persist_directory="./chroma_db", embedding_function=embed_model)

# 5.查询向量数据库
query = "1937年北京大学发生了什么？"
result = chroma_db.similarity_search(query, k=3) # 返回topK个最相似的文档
print(f'result->{result}')