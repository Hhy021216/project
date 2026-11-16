# coding:utf-8
import gradio as gr
import time
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
import os

# 全局变量存储向量数据库
current_db = None


def create_vector_db_from_file(file_path):
    """
    从上传的文件创建向量数据库
    支持 txt, pdf, docx 格式
    """
    try:
        if file_path.endswith('.txt'):
            from langchain_community.document_loaders import TextLoader
            loader = TextLoader(file_path, encoding='utf-8')
        elif file_path.endswith('.pdf'):
            from langchain_community.document_loaders import PyPDFLoader
            loader = PyPDFLoader(file_path)
        elif file_path.endswith('.docx'):
            from langchain_community.document_loaders import Docx2txtLoader
            loader = Docx2txtLoader(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_path}")

        documents = loader.load()
        # 文本分割
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        texts = text_splitter.split_documents(documents)

        # 创建向量数据库
        embeddings = OllamaEmbeddings(model="mxbai-embed-large", temperature=0)
        db = FAISS.from_documents(texts, embeddings)
        FAISS.save_local(db, "faiss/logistics")
        return db
    except Exception as e:
        raise e


def load_default_db():
    """
    加载默认的向量数据库
    """
    global current_db
    try:
        embeddings = OllamaEmbeddings(model="mxbai-embed-large", temperature=0)
        current_db = FAISS.load_local("faiss/logistics", embeddings, allow_dangerous_deserialization=True)
    except Exception as e:
        print(f"加载默认向量数据库失败: {e}")
        current_db = None


def handle_file_upload(file_obj):
    """
    处理文件上传并创建向量数据库
    """
    global current_db
    try:
        if file_obj is None:
            return "未选择文件", None

        file_path = file_obj.name
        current_db = create_vector_db_from_file(file_path)
        return f"成功加载文件: {os.path.basename(file_path)}", current_db is not None
    except Exception as e:
        return f"处理文件时出错: {str(e)}", None


def get_related_content(related_docs):
    """
    提取相关文档内容
    """
    related_content = []
    for doc in related_docs:
        related_content.append(doc.page_content.replace("\n\n", "\n"))
    return "\n".join(related_content)


def answer_question(question):
    """
    回答用户提出的问题
    """
    global current_db
    start_time = time.time()

    try:
        # 如果没有加载向量数据库，则尝试加载默认数据库
        if current_db is None:
            embeddings = OllamaEmbeddings(model="mxbai-embed-large", temperature=0)
            current_db = FAISS.load_local("faiss/logistics", embeddings, allow_dangerous_deserialization=True)

        # 搜索相关文档
        docs = current_db.similarity_search(question, k=2)
        related_content = get_related_content(docs)

        # 构建提示词模板
        PROMPT_TEMPLATE = """
        基于以下已知信息，简洁和专业的来回答用户的问题。不允许在答案中添加编造成分。
        已知内容:
        {context}
        问题:
        {question}"""

        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=PROMPT_TEMPLATE,
        )

        formatted_prompt = prompt.format(context=related_content, question=question)

        # 使用模型生成答案
        model = OllamaLLM(model="qwen3:4b")
        result = model.invoke(formatted_prompt)
        print(f'>>>答案：{result}')

        end_time = time.time()
        retrieved_content_output = related_content[:500] + "..." if len(related_content) > 500 else related_content
        # 返回答案和相关信息
        return result, f"{end_time - start_time:.4f}s", retrieved_content_output
    except Exception as e:
        end_time = time.time()
        return f"处理过程中出现错误: {str(e)}", f"{end_time - start_time:.4f}s", ""


def create_gradio_interface():
    """
    创建Gradio界面
    """
    with gr.Blocks(title="智能物流助手") as demo:
        gr.Markdown("# 🚚 智能物流助手")
        gr.Markdown("基于向量数据库的物流信息查询系统")

        with gr.Row():
            with gr.Column():
                # 文件上传组件
                file_input = gr.File(
                    label="上传知识库文件",
                    file_types=['.txt', '.pdf', '.docx'],
                    file_count="single"
                )
                upload_btn = gr.Button("加载文件到知识库")
                upload_status = gr.Textbox(label="上传状态", interactive=False)

                question_input = gr.Textbox(
                    label="请输入您的物流问题",
                    placeholder="例如：我的快递出发地是哪？预计几天的时间到达？",
                    lines=3
                )

                submit_btn = gr.Button("获取答案", variant="primary")

                # 示例问题
                gr.Examples(
                    examples=[
                        "我的快递出发地是哪？",
                        "预计几天的时间到达？",
                        "我的订单状态如何？",
                        "物流信息是什么？"
                    ],
                    inputs=question_input
                )

            with gr.Column():
                processing_time_output = gr.Textbox(
                    label="处理时间",
                    interactive=False
                )
                retrieved_content_output = gr.Textbox(
                    label="检索到的相关内容",
                    lines=10,
                    interactive=False
                )
                answer_output = gr.Textbox(
                    label="AI回答",
                    lines=8,
                    interactive=False
                )

        # 事件绑定
        upload_btn.click(
            fn=handle_file_upload,
            inputs=file_input,
            outputs=[upload_status, gr.State()]
        )

        submit_btn.click(
            fn=answer_question,
            inputs=question_input,
            outputs=[answer_output, processing_time_output, retrieved_content_output]
        )

    return demo


if __name__ == "__main__":
    # 初始化时加载默认数据库
    load_default_db()
    interface = create_gradio_interface()
    interface.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,  # 设为True可创建公共链接
        debug=True
    )
