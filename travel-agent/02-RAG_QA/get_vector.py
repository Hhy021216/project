"""
演示
    RAG系统的离线部分：由知识库生成向量数据库。
工作流程：
    知识库 -> 文档加载 -> 文本分割 -> 嵌入 -> 向量数据库
"""
from langchain_community.document_loaders import PyMuPDFLoader
# from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

# 1.定义函数，生成向量数据库
def get_vector_db():
    # 1.加载文档
    # loader = UnstructuredLoader("物流信息.txt")
    loader = PyMuPDFLoader("物流信息.pdf")
    data = loader.load()
    print(f'data->{data}')
    # 2.文本分割
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=128,
        chunk_overlap=4)
    chunks = text_splitter.split_documents(data)
    # 3.创建Embedding模型
    embed_model = OllamaEmbeddings(model="mxbai-embed-large")

    # 4.生成向量数据库
    vector_db = FAISS.from_documents(chunks, embed_model)
    vector_db.save_local("./faiss/logistics")
    print(f'向量数据库保存成功')
    return chunks

# 主程序
if __name__ == '__main__':
    get_vector_db()
