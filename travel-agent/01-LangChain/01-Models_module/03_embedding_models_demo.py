"""
演示
    嵌入模型 Embedding Models 的用法
    作用：文本向量化
涉及到的API:
    OllamaEmbeddings
"""
from langchain_ollama import OllamaEmbeddings

# 1.实例化模型
model = OllamaEmbeddings(model="mxbai-embed-large", temperature=0)
# 2.对单个文本进行嵌入
res1 = model.embed_query('这是第一个测试文档')
print(f'result1->{res1}')
print(f'result1的长度->{len(res1)}')
# 3.对多个文本进行批量嵌入编码
res2 = model.embed_documents(['这是第一个测试文档', '这是第二个测试文档'])
print(len(res2))
print(len(res2[0]))