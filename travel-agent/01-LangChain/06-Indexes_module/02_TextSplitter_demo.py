"""
演示
    TextSplitter 文本分割器的使用
    文本分割器：将长文本分割成小片段，以便更好地处理和分析。
涉及的API:
    CharacterTextSplitter 字符文本分割器
"""

# 1.字符文本分割
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.documents import Document
# 1.1 创建 文本分割器，指定分割符和分割长度
text_splitter = CharacterTextSplitter(
    separator=" ", # 分割符
    chunk_size=5, # 分割长度，文本块最大长度
    chunk_overlap=1, # 每个块之间的重叠长度
)

# 1.2 单文本分割
result1 = text_splitter.split_text("a b c d e f")
print(f'result1->{result1}')

# 1.3 多文本分割，返回Document对象列表
result2 = text_splitter.create_documents(["a b c d e f", "e f g h"])
print(f'result2->{result2}')

# 1.4 文档分割，指定元数据
result3 = text_splitter.split_documents(
    [Document(page_content="a b c d e f", metadata={"id": "1"}),
    Document(page_content="1 2 3 4", metadata={"id": "2"})],
)
print(f'result3->{result3}')
#
# # 2.递归字符文本分割
# from langchain_text_splitters import RecursiveCharacterTextSplitter
#
# # 2.1 创建 文本分割器 对象，指定分割符和分割长度
# text_splitter = RecursiveCharacterTextSplitter(
#     separators=["\n\n", "\n", " ", ""], # 分割符
#     chunk_size=20, # 分割长度，每个块最大长度
#     chunk_overlap=2, # 每个块之间的重叠长度
#     length_function=len, # 长度函数
# )
#
# # 2.2 文本分割
# text = """
# 人工智能正在快速发展，尤其是大语言模型的应用，正在改变人类的工作方式。
# 它们可以帮助人们进行写作、代码生成、甚至是科研探索。
# 相比之下，新能源的发展同样重要。
# 电动车和太阳能正在逐渐替代传统能源，减少碳排放，对全球环境保护至关重要电动车和太阳能正在逐渐替代传统能源，减少碳排放，对全球环境保护至关重要电动车和太阳能正在逐渐替代传统能源，减少碳排放，对全球环境保护至关重要。
# """
# result1 = text_splitter.split_text(text)
# print(f'result1->{result1}')
#
# # 3.语义文本分割
# from langchain_experimental.text_splitter import SemanticChunker
# from langchain_ollama import OllamaEmbeddings
#
# # 3.1 创建 Ollama 模型对象
# embed_model = OllamaEmbeddings(model="mxbai-embed-large")
#
# # 3.2 创建 文本分割器 对象，指定分割长度和重叠长度
# text_splitter = SemanticChunker(
#     embeddings=embed_model, # 嵌入模型
#     breakpoint_threshold_type='percentile',
#     breakpoint_threshold_amount=20.0,   # 更低的百分位会更“积极”地切分（数值越小 => 切得越多）
#     sentence_split_regex=r'(?<=[。！？.!?])\s*',   # 句子拆分正则为同时识别中/英文终结符
#     min_chunk_size=10,  # 最小块大小
# )
#
# text = """
# 人工智能正在快速发展，尤其是大语言模型的应用，正在改变人类的工作方式。
# 它们可以帮助人们进行写作、代码生成、甚至是科研探索。
# 相比之下，新能源的发展同样重要。
# 电动车和太阳能正在逐渐替代传统能源，减少碳排放，对全球环境保护至关重要。
# 英雄联盟的亚索草率
# """
# # 3.3 语义文本分割
# docs = text_splitter.split_text(text)
# for i, d in enumerate(docs):
#     print(f"----- Chunk {i} -----")
#     print(d)
#     print()

# 4.Markdown文本分割
# from langchain_text_splitters import MarkdownHeaderTextSplitter
#
# # 4.1 创建 文本分割器 对象
# headers_to_split_on = [
#     ("#", "title1"),
#     ("##", "title2"),
#     ("###", "title3"),
# ]
# text_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
#
# # 4.2 文本分割
# text = "# Header 01\nSome text\n## Header 02\nMore text\n### Header 03\nEven more text"
# docs = text_splitter.split_text(text)
# print(docs)