# 教育 RAG Demo

面向 IT 教培场景的教学资料问答系统。核心价值不是"接一个向量库"，而是**完整的分流链路与降级设计**——不是所有问题都该走 RAG。

## 架构

```
用户提问
   │
   ├─ 寒暄 / 问候 ────────────→ 规则直答（greeting.py）
   ├─ FAQ 语义匹配 ──────────→ 高置信命中，直接返回标准答案（faq.py）
   ├─ 知识库置信不足 ────────→ Web 搜索兜底（web_search.py / fallback.py）
   └─ 其余 ─────────────────→ 混合检索 → 重排 → 生成带引用回答（rag.py）
```

### 两条链路，不可混淆

| 链路 | 数据来源 | 触发条件 | 执行位置 |
|------|---------|---------|---------|
| FAQ 分流 | MySQL 中的标准问答对 | 用户问题与标准问题语义匹配达到高置信 | 应用层匹配，命中即返回 |
| 混合检索 | Milvus 中的知识文档切片 | FAQ 未命中，进入 RAG | 向量 + 稀疏双路召回后融合 |

> FAQ 存在 MySQL 不代表在 MySQL 里做语义检索——数据库只负责存储，匹配发生在应用层。

## 目录结构

```
edu-rag-demo/
├── app.py              # FastAPI 入口
├── routes.py           # 路由定义
├── pipeline.py         # 主链路编排：分流 → 检索 → 生成
├── config.py           # 配置中心（读 .env）
├── prompts.py          # 提示词模板
├── logger.py           # 日志
├── cli.py              # 命令行批处理入口
├── alembic.ini         # 数据库迁移配置
├── alembic/            # 迁移脚本
├── db/                 # 连接与模型
├── services/
│   ├── greeting.py     # 寒暄识别与直答
│   ├── faq.py          # FAQ 语义匹配
│   ├── rag.py          # 混合检索 + 生成
│   ├── tfidf.py        # 稀疏检索（jieba 分词 + TF-IDF）
│   ├── chunk_store.py  # 切片存储
│   ├── fallback.py     # 拒答 / 兜底策略
│   └── web_search.py   # 联网搜索兜底
├── storage/
│   ├── data/           # 知识库源文档
│   └── logs/           # 运行日志（不入库）
└── templates/          # 调试页面
```

## 技术栈

| 层面 | 选型 |
|------|------|
| Web 框架 | FastAPI + Jinja2 |
| 关系数据库 | MySQL + SQLAlchemy + Alembic |
| 向量数据库 | Milvus（pymilvus） |
| 缓存 | Redis |
| 稀疏检索 | jieba 分词 + TF-IDF（scikit-learn） |
| 文档解析 | unstructured |
| 大模型 | OpenAI 兼容接口（默认 DashScope / qwen-plus） |

## 快速开始

### 1. 准备依赖服务

```bash
# Milvus（Docker 方式，含 etcd / minio）
docker run -d --name milvus-standalone -p 19530:19530 -p 9091:9091 milvusdb/milvus:latest standalone

# MySQL 与 Redis 用你本机已有的实例即可
```

### 2. 安装依赖

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 配置

```bash
cp .env.example .env
# 按实际情况填写 MySQL / Milvus 连接信息与大模型 API Key
```

### 4. 建表与建库

```bash
alembic upgrade head      # 初始化 MySQL 表结构
# 知识库入库：调用 services 中的解析与切片流程，或使用 cli.py
```

### 5. 启动

```bash
uvicorn app:app --reload --port 8000
```

浏览器打开 `http://localhost:8000` 使用内置调试页；也可用 `python cli.py` 走命令行批处理。

## 可观测

- 全链路日志落盘至 `storage/logs/app.log`（已加入 .gitignore）
- 检索过程记录命中来源与分数，便于定位是 FAQ 命中、向量召回还是搜索兜底

## 注意事项

- `.env` 含数据库密码与 API Key，**不入库**
- `storage/logs` 与向量库缓存目录均已在 `.gitignore` 中排除
- 首次运行需自行导入知识文档，仓库内的 `storage/data` 仅为示例资料
