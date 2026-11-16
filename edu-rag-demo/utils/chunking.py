"""文档加载与切分。
- md/txt：读文本后按 CHUNK_SIZE 切块
- CSV：按表头拼装成区块（不二次切分）
- 其他：先 UnstructuredLoader.load，再按 CHUNK_SIZE 切块
"""
import pandas as pd
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_unstructured import UnstructuredLoader

from config import config
from logger import logger


def load_text_and_chunk(file_path):
    file_path = Path(file_path)
    # 读取文件，防止编码报错，指定编码为utf-8，去除两端空格
    text = file_path.read_text(encoding="utf-8").strip()

    # 定义递归文本切分器
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""],
    )
    # 用切分器切分文本
    splits = splitter.split_text(text)

    docs = []
    for i, chunk in enumerate(splits):
        docs.append(
            Document(
                page_content=chunk,
                metadata={
                    "file_name": file_path.name,
                    # 切分之后的第几块
                    "index": i,
                },
            )
        )
    logger.info(f"从 {file_path.name} 切分得到 {len(docs)} 个块")
    return docs


def load_csv_and_chunk(file_path):
    # file_path Path类的一个对象
    df = pd.read_csv(file_path, encoding="utf-8")

    docs = []
    for index, row in df.iterrows():
        # 分类:入职与考勤
        # 问题:入职体检费用什么时候报销？
        # 答案:职体检费用可在转正后 45 天以内申请报销

        # lst = []
        # for col in df.columns:
        #     lst.append(col + ':' + row[col])
        # print('\n'.join(lst))

        chunk = '\n'.join([f'{col}: {row[col]}' for col in df.columns])
        docs.append(
            Document(
                page_content=chunk,
                metadata={
                    "file_name": file_path.name,
                    "index": index,
                },
            )
        )
    logger.info(f"从 {file_path.name} 切分得到 {len(docs)} 个块")
    return docs


def load_file_and_chunk(file_path):
    # 加载完文件之后，是按页码进行切割的
    loader = UnstructuredLoader(file_path)
    raw_docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""],
    )
    # 对于单页内容比较多的块，进行进一步切分
    split_docs = splitter.split_documents(raw_docs)

    docs = []
    for i, doc in enumerate(split_docs):
        docs.append(
            Document(
                page_content=doc.page_content,
                metadata={
                    "file_name": file_path.name,
                    "index": i,
                },
            )
        )

    logger.info(f"从 {file_path.name} 切分得到 {len(docs)} 个块")
    return docs


def load_and_chunk(file_path):
    """加载单个文件，返回 Document 列表：按后缀分发。"""
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(file_path)

    # suffix 后缀
    suffix = file_path.suffix.lower()
    if suffix in [".md", ".txt"]:
        return load_text_and_chunk(file_path)
    if suffix == ".csv":
        return load_csv_and_chunk(file_path)
    else:
        return load_file_and_chunk(file_path)
