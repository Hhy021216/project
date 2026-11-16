# 项目集合 · Projects

> 何航渝（Hhy021216）· 大模型应用 / Agent 开发方向
>
> 本仓库集中存放我的四个实践项目：RAG 检索系统、多智能体平台、浏览器 AI 插件与 LangChain 工程实践。
> 每个项目独立成目录，互不依赖，可单独阅读与运行。

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?logo=langchain&logoColor=white)](https://www.langchain.com/)
[![Vue3](https://img.shields.io/badge/Vue3-4FC08D?logo=vuedotjs&logoColor=white)](https://vuejs.org/)

---

## 目录导航

| # | 项目 | 中文名 | 一句话定位 | 技术栈 |
|---|------|--------|-----------|--------|
| 1 | [edu-rag-demo](./edu-rag-demo/) | 教育 RAG Demo | 教学资料问答：FAQ 分流 → 混合检索 → 精排 → 兜底 | FastAPI · Milvus · MySQL · Redis · BGE |
| 2 | [boss-eq-reply](./boss-eq-reply/) | 回复助手 | 招聘会话的 AI 高情商回复插件（只辅助，不代发） | Chrome MV3 · 原生 JS · DeepSeek |
| 3 | [edu-agent](./edu-agent/) | 教育智能体 Demo | 四大业务 Agent + Orchestrator 编排的教培 AI 平台 | LangChain · LangGraph · FastAPI · Vue3 |
| 4 | [travel-agent](./travel-agent/) | 旅游智能体 Demo | LangChain 七大模块逐项实践 + RAG 问答闭环 | LangChain · Chroma · BM25 · Streamlit |

---

## 1. 教育 RAG Demo

[`edu-rag-demo/`](./edu-rag-demo/) · [项目 README](./edu-rag-demo/README.md)

面向 IT 教培场景的检索增强问答系统。核心不在"接个向量库"，而在**完整的分流链路与降级设计**——不是所有问题都该走 RAG。

```
用户提问
   │
   ├─ 寒暄/问候 ──────→ 规则直答
   ├─ FAQ 语义匹配 ───→ 高置信命中，直接返回标准答案
   ├─ 知识库不足 ─────→ Web 搜索兜底
   └─ 其余 ───────────→ 混合检索（向量 + TF-IDF）→ 重排 → 生成带引用回答
```

**技术要点**
- FAQ 与知识库是两条独立链路：FAQ 存 MySQL，应用层做语义匹配，命中即返回；未命中才进入 RAG
- 混合检索：Dense（BGE-M3）+ Sparse（TF-IDF/jieba）双路召回后融合
- 全链路可观测：`storage/logs` 落盘，Alembic 管理表结构演进
- FastAPI + Jinja2 内置调试页，`cli.py` 支持无界面批处理

---

## 2. 回复助手（BOSS 高情商回复助手）

[`boss-eq-reply/`](./boss-eq-reply/) · [项目 README](./boss-eq-reply/README.md)

Chrome Manifest V3 扩展。在招聘平台会话页读取当前对话与简历项目经历，调用大模型生成**三条**可直接复制的高情商回复。

**设计原则**
- **只辅助，不自动发送**——所有回复需人工确认复制，避免误发风险
- 最小权限：仅 `storage` + `clipboardWrite`，host 权限白名单绑定目标站点与模型 API
- 内容脚本注入 + 侧边面板，不侵入原页面 DOM 结构
- CSP 锁定 `script-src 'self'`，禁用远程脚本执行
- 设置页支持自定义模型服务商与 API Key（本地存储）

| 文件 | 职责 |
|------|------|
| `manifest.json` | MV3 声明：权限、注入规则、CSP |
| `background.js` | Service Worker，统一转发模型请求 |
| `loader.js` / `panel.js` | 页面注入与面板 UI |
| `reader.js` | 会话与简历内容提取 |
| `core.js` | 提示词编排与回复生成 |
| `options.*` | 配置界面 |

---

## 3. 教育智能体 Demo（EduAgent）

[`edu-agent/`](./edu-agent/) · [项目 README](./edu-agent/README.md)

面向 IT 教培机构的 AI 原生教学辅助平台。把四类高频重复业务各自封装为独立 Agent，再由 Orchestrator 统一做意图路由。

| Agent | 业务能力 | 核心范式 |
|-------|---------|---------|
| 智能问答 QA | 课程知识库答疑 | RAG 混合检索 + BGE-M3 + Reranker + SSE 流式 |
| 试卷批改 Exam | 选择/简答/编程题批改 | 三轨并行批改 + HitL 教师确认环 |
| 简历审查 Resume | 六维度评分与建议 | PDF 解析 + 结构化抽取 + 并行评分 |
| 模拟面试 Interview | 五阶段技术面试陪练 | 状态机对话 + Think Tool 双轨评估 |

**技术栈**：LangChain 1.2.10 + LangGraph 1.0.9 + FastAPI（SSE）· Milvus + PostgreSQL + Redis + MinIO · Vue3 + TypeScript + Element Plus
**本地模型**：BGE-M3（dense + sparse 双输出）、BGE-Reranker-large、MiniLM-L6-v2 意图分类，均为进程内调用

> ⚠️ **模型权重未入库**。`backend/models/` 目录已排除（约 4.6 GB），运行前请按 [edu-agent/README.md](./edu-agent/README.md) 中的说明自行下载并放置到对应路径。

---

## 4. 旅游智能体 Demo

[`travel-agent/`](./travel-agent/) · [项目 README](./travel-agent/README.md)

LangChain 工程能力的系统练习：从 Models、Prompts、Chains、Output Parsers、Memory、Indexes 到 Agent 七大模块，逐项落地可运行示例，最终收口到一个完整的 RAG 问答应用。

```
travel-agent/
├── 01-LangChain/           # 七大模块逐项 Demo
│   ├── 01-Models_module/       LLM / ChatModel / Embedding
│   ├── 02-Prompts_module/      Zero-shot / Few-shot / ChatPrompt
│   ├── 03-Chains_module/       LLMChain / 多链串联
│   ├── 04-Output_parsers/      Str / List / Json / Pydantic / 自定义
│   ├── 05-Memory_module/       会话历史与短期记忆
│   ├── 06-Indexes_module/      文档加载 / 切分 / 向量化 / 检索
│   └── 07-Agent_module/        Agent 构建与工具调用
└── 02-RAG_QA/              # RAG 问答完整应用（物流领域示例）
    ├── get_vector.py           建库：文档 → 切分 → 向量化 → Chroma
    ├── logistics_assistant_main.py   CLI 版问答
    └── logistics_assistant_web.py    Streamlit Web 版
```

**技术要点**：Chroma 向量库 + BM25 稀疏检索 + sentence-transformers 嵌入 + Streamlit 交互界面。

---

## 仓库说明

### 目录约定
- 每个项目自成目录，含独立 `README.md` 与依赖清单
- 敏感配置一律不入库，各项目提供 `.env.example` 作为模板
- 模型权重、向量库缓存、`node_modules`、虚拟环境均已通过 `.gitignore` 排除

### 本地运行通用步骤
```bash
git clone https://github.com/Hhy021216/project.git
cd project
cd <项目目录>          # 进入任一子项目
cp .env.example .env   # 填写你自己的 Key
pip install -r requirements.txt
```

详细启动方式见各子项目 README。

---

## 联系方式

- GitHub：[@Hhy021216](https://github.com/Hhy021216)
- 方向：Agent 开发（多 Agent 系统）· RAG 检索架构 · 大模型微调 · CV / 多模态
