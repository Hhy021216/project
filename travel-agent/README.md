# 旅游智能体 Demo

LangChain 工程能力的系统练习仓库：七大核心模块逐项落地为可运行示例，最终收口到一个完整的 RAG 问答应用。

> 说明：项目名沿用"旅游智能体"的命名，当前 `02-RAG_QA` 中的完整应用以**物流信息问答**作为领域示例，链路结构可直接迁移到旅游场景（景点介绍、路线攻略、票务规则等）。

## 目录结构

```
travel-agent/
├── requirements.txt
├── .env.example
├── 01-LangChain/                    # 七大模块逐项 Demo
│   ├── 01-Models_module/            # LLM / ChatModel / Embedding 三类模型接口
│   ├── 02-Prompts_module/           # Zero-shot / Few-shot / ChatPrompt 模板
│   ├── 03-Chains_module/            # 单链与多链串联
│   ├── 04-Output_parsers/           # Str / List / Json / Pydantic / 自定义解析器
│   ├── 05-Memory_module/            # 会话历史与短期记忆
│   ├── 06-Indexes_module/           # 文档加载 → 切分 → 向量化 → 检索
│   └── 07-Agent_module/             # Agent 构建与工具调用
└── 02-RAG_QA/                       # RAG 问答完整应用（物流领域示例）
    ├── get_vector.py                # 建库：PDF/TXT → 切分 → 嵌入 → Chroma
    ├── logistics_assistant_main.py  # CLI 版问答
    ├── logistics_assistant_web.py   # Streamlit Web 版
    ├── 物流信息.pdf / .txt          # 示例知识源
```

## 七大模块对应关系

| 模块 | 关键内容 | 示例文件 |
|------|---------|---------|
| Models | `OllamaLLM` / `ChatOpenAI` / `Embeddings` 的实例化与调用差异 | `01-Models_module/*.py` |
| Prompts | 模板变量替换、few-shot 示例注入、Chat 消息角色组装 | `02-Prompts_module/*.py` |
| Chains | 链式调用与多链组合，数据在环节间流转 | `03-Chains_module/*.py` |
| Output Parsers | 把模型自由文本转为结构化数据（含 Pydantic 校验与自定义解析） | `04-Output_parsers/*.py` |
| Memory | 历史消息窗口与短时记忆保持 | `05-Memory_module/*.py` |
| Indexes | Unstructured 加载、TextSplitter 切分、向量化与 Retriever | `06-Indexes_module/*.py` |
| Agent | Agent 构建、工具注册与多步推理 | `07-Agent_module/*.py` |

## 技术栈

| 层面 | 选型 |
|------|------|
| 编排框架 | LangChain（含 community / openai / ollama / chroma 等子包） |
| 模型接入 | Ollama 本地模型 + OpenAI 兼容接口（DeepSeek 等） |
| 向量库 | Chroma |
| 稀疏检索 | rank_bm25 |
| 嵌入模型 | sentence-transformers（本地）/ modelscope |
| 文档解析 | unstructured + pymupdf + PyPDF2 |
| 交互界面 | Streamlit / Gradio |

## 快速开始

### 1. 安装依赖

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置模型

```bash
cp .env.example .env
# 填入你的 API Key；若使用 Ollama 本地模型，请先 ollama pull 对应模型
```

### 3. 逐模块运行

```bash
cd 01-LangChain/01-Models_module
python 01_llms_demo.py
```

### 4. 运行 RAG 问答

```bash
cd 02-RAG_QA

# 第一步：构建向量库
python get_vector.py

# 第二步：命令行提问
python logistics_assistant_main.py

# 或启动 Web 界面
streamlit run logistics_assistant_web.py
```

## 检索策略

`02-RAG_QA` 采用向量检索 + BM25 稀疏检索的组合：

- **Dense**：sentence-transformers 生成句向量，Chroma 做相似度召回
- **Sparse**：rank_bm25 基于词频匹配，弥补专有名词与精确查询的召回缺口
- 两路结果融合后送入模型生成答案，并保留来源片段引用

## 注意事项

- `.env` 含 API Key，**不入库**（仓库仅提供 `.env.example`）
- `chroma_db/` 为本地向量库缓存，已在 `.gitignore` 中排除，首次运行由 `get_vector.py` 重建
- Ollama 相关示例需本地已启动 Ollama 服务并拉取对应模型
