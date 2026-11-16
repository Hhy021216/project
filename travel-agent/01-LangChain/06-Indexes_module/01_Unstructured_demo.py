"""
演示
    unstructured 文档加载器的使用
涉及的API:
    UnstructuredLoader
    TextLoader
"""
from langchain_unstructured import UnstructuredLoader

# 1.创建 UnstructuredLoader 对象
loader = UnstructuredLoader('./data/衣服属性.txt', encoding='utf8')
docs = loader.load()
print(f'docs->{docs}')
print(f'len->{len(docs)}')
print(f'第一行数据->{docs[0].page_content}')

# 社区集成包
from langchain_community.document_loaders import TextLoader
# 2.创建 TextLoader 对象
loader = TextLoader('./data/衣服属性.txt', encoding='utf8')
docs = loader.load()
print(f'docs->{docs}')
print(f'len->{len(docs)}')
print(f"第一行数据->{docs[0].page_content.split('\n')[0]}")
