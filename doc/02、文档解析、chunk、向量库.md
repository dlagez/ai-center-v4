可以，我按 **“一个服务，多个模块”** 给你出一版**基于 LangChain 的文档解析子系统技术方案**。
我会尽量贴着 LangChain 官方推荐的链路来设计，但结合你的当前诉求做调整：**Document Loader → Normalize → DOC_CHUNKS → Embedding → Vector Store / Retriever → RAG**；`chunking` 作为后续扩展模块预留，第一阶段不实现。复杂检索流程和可恢复编排则交给 **LangGraph**。LangChain 官方文档也明确把 document loader、embedding、vector store 抽象作为知识库与检索的基础，而 LangGraph 重点负责 durable execution、streaming、human-in-the-loop 等运行时能力。([LangChain Docs][1])

---

# 一、目标定位

这个子系统建议你先作为**当前仓库内的独立业务子系统**来组织，职责很清楚：

1. 接收 `data/` 目录中的文档路径，或外部文档 URL。
2. 当前通过 Docling 解析器把文件统一转换成标准 `DOC_CHUNKS`。
3. 做清洗、元数据补充，并保留其他输出格式，供后续 `processing/chunking` 模块接入。
4. 将 `DOC_CHUNKS` 直接写入向量库和检索索引。
5. 对外提供解析 / 入库 / 检索 / RAG / 重建索引接口。

这么做的好处是：你把“文档解析”从大中台里抽成一个边界清晰的能力服务，后面不管上层是 Chat、Agent、知识助手还是合同助手，都走同一个入口。这个设计符合 LangChain 官方把 loader、splitter、retriever 做成可替换模块的思路。([LangChain Docs][1])

---

# 二、推荐技术架构

## 1. 总体技术选型

我建议这一个服务内部这样分层：

* **API 层**：FastAPI
* **应用编排层**：LangGraph
* **processing 域**：统一承载 loaders / normalize / chunking，避免解析策略横向膨胀
* **检索层**：LangChain Retriever 抽象
* **生成层**：RAG 问答链路
* **索引层**：Qdrant
* **模型适配层**：LangChain Embeddings / Chat Model 接口
* **任务层**：异步任务队列
* **元数据存储层**：SQLite（可替换为 Postgres）
* **输入源层**：`data/` 目录或 URL

这里面和 LangChain 官方最一致的部分是：**解析结果先标准化，再进入 embed / vector store / retriever 链路**。在当前方案里，Docling 的标准入库输出定为 `DOC_CHUNKS`，直接进入 embedding 和向量库；文档加载器依然是标准入口，但在工程组织上建议把 `loaders / normalize / chunking` 收敛到 `processing` 域里，避免以后解析器和处理策略越来越多时目录横向膨胀。([LangChain Docs][1])

---

## 2. 文档解析主策略

### 主解析器：Docling

Docling 的 LangChain 集成页明确说明，它适合解析 **PDF、DOCX、PPTX、HTML** 等格式，并输出带有**版面、表格等 richer representation** 的内容；官方还提供 `DoclingLoader`。对于企业知识库里的制度、合同、标书、方案、汇报材料，这条线最合适。当前方案里，**Docling 的标准输出格式明确为 `DOC_CHUNKS`**，用于直接入向量库。([LangChain Docs][2])


### 推荐解析策略

当前第一阶段先固定使用 **Docling**：

* Office / 高质量 PDF / HTML：统一走 **Docling**

后续如果再接其他解析器，再补解析器路由层即可。这也和 LangChain 官方“loader 是标准化入口、可自由替换”的设计一致。([LangChain Docs][1])

### 输出格式约定

第一阶段统一约定：

* **标准入库格式**：`DOC_CHUNKS`
* **标准入库路径**：`DOC_CHUNKS` → embedding → vector store
* **其他保留输出**：Markdown / Text / Structured JSON / LangChain `Document` 等兼容格式按需导出，但不进入第一阶段主入库链路

这样做的好处是：

* Docling 输出后不再额外做一次 `processing/chunking`
* 向量库入库链路更短，减少中间转换
* 后续如果要接自定义 `processing/chunking`，可以直接消费保留下来的其他格式输出

---

# 三、模块划分

我建议一个服务拆成下面 9 个一级模块，其中 `processing` 是文档处理域，`retrieval` 和 `rag` 明确分离。

## 1. `api` 模块

职责：

* 提供解析、重建索引、查询、任务状态查询接口
* 对外只暴露业务语义，不暴露内部解析器细节

建议接口：

* `POST /documents/parse`
* `POST /documents/index`
* `POST /documents/reindex`
* `GET /documents/{id}`
* `POST /search`，支持 `query + metadata_filter`
* `POST /rag/query`，支持 `query + metadata_filter`
* `GET /jobs/{job_id}`

这个模块就是服务边界，不承担解析逻辑本身。

---

## 2. `ingestion` 模块

职责：

* 解析输入源
* 支持 `data/` 目录文件路径或 URL
* 文件类型识别
* 去重（hash）
* 生成解析任务

这个模块只关心“文档来源进入处理链路”，不负责文件持久化存储。

---

## 3. `processing` 域

职责：

* 统一承载 `loaders / normalize / chunking`，避免以后解析策略越来越多时目录横向膨胀
* 对内组织解析器实现、标准化逻辑、切分扩展点
* 对外只暴露稳定的 `DOC_CHUNKS` 和兼容导出格式

建议内部按子域组织：

* `processing/loaders/`：封装 LangChain Document Loader；第一阶段只保留 Docling 实现
* `processing/normalize/`：轻量标准化逻辑；第一阶段仅保留必要校验/补值
* `processing/chunking/`：预留的切分能力；第一阶段不实现

其中 `processing/loaders/` 第一阶段承担的职责是：

* 输出标准 `DOC_CHUNKS`
* 按需保留其他格式输出能力

当前阶段目录建议只保留：

* `processing/loaders/base.py`
* `processing/loaders/docling_loader.py`

如果后续接第二种解析器，再补 `router.py` 和其他 loader 实现即可。

LangChain 官方明确说 document loaders 的作用是把不同来源的数据统一转成标准化结果，这一层建议你做成“**主输出一个 `DOC_CHUNKS`，附带若干兼容格式**”的抽象，这样最符合当前入库目标，也方便后续扩展。([LangChain Docs][1])

`processing/normalize/` 第一阶段不建议做成重模块，但建议至少保证这些 metadata 字段完整：

* `document_id`
* `source`
* `file_name`
* `file_type`
* `page`
* `section_title`
* `chunk_id`
* `chunk_index`
* `parser`
* `tenant_id`
* `knowledge_base_id`

`processing/chunking/` 当前阶段不实现，原因很简单：**Docling 标准输出已经确定为 `DOC_CHUNKS`，可以直接入向量库，不需要再额外切块**。

如果后续需要处理非 `DOC_CHUNKS` 输出，可以按 LangChain splitter 的建议接入：

* Markdown：`MarkdownHeaderTextSplitter` → `RecursiveCharacterTextSplitter`
* HTML：`HTMLHeaderTextSplitter` / `HTMLSectionSplitter` → `RecursiveCharacterTextSplitter`
* 纯文本：直接 `RecursiveCharacterTextSplitter`

这正对应了 LangChain 官方 splitter 文档给出的使用方式，但这一部分放到第二阶段实现。([LangChain Docs][5])

---

## 4. `embedding` 模块

职责：

* 调 embedding 模型
* 支持批量 embedding
* 控制重试、限流、缓存

这里不要把具体模型写死。
只保留一个统一接口，例如：

* `embed_documents(doc_chunks)`
* `embed_query(query)`

这样后面不管你走本地 embedding、vLLM embedding、OpenAI-compatible embedding，都不改上层。

---

## 5. `indexing` 模块

职责：

* 将 `DOC_CHUNKS` 和向量写入向量库
* 建立 collection / namespace
* 处理更新、删除、重建索引

这里建议你把“索引构建”理解为一条流水线，而不是单独一个组件。
LangChain 官方知识库教程本身也是 document loader + embedding + vector store 这条线。([LangChain Docs][6])

---

## 6. `retrieval` 模块

职责：

* 统一对上层暴露 retriever，而不是暴露底层 vector store
* 基于 Qdrant 构造 retriever，内部通过 `as_retriever()` 适配检索能力
* 支持 hybrid retrieval
* 将 metadata filter 作为一等公民纳入检索接口
* 支持 rerank
* 只负责召回、过滤、排序，不负责答案生成

LangChain 官方把 retriever 作为单独抽象，而 retrieval 文档也明确区分了 2-Step RAG、Agentic RAG、Hybrid 三种架构。你的子系统第一阶段建议先走 **2-Step RAG**，因为它更简单、可预测、延迟更稳。([LangChain Docs][7])

这里建议你在设计上明确两条约束：

* **上层只依赖 retriever**：API、RAG 服务层、业务服务层都不直接操作 Qdrant vector store，只通过 `retrieval/service.py` 或 `retrieval/retriever_factory.py` 获取 retriever
* **filter 进入检索主接口**：`metadata_filter` 直接成为 `/search` 和 `/rag/query` 的标准入参，而不是后续补丁能力

这样后面做这些过滤会更自然：

* `tenant_id`
* `knowledge_base_id`
* `doc_type`
* `page`
* `document_id`

这也更贴合 Qdrant 的 LangChain 集成能力：Qdrant 可以作为 vector store 使用，也可以直接转换成 retriever；同时其过滤能力可以直接融入 LangChain 检索调用。([LangChain Docs][9])

---

## 7. `rag` 模块

职责：

* 承接生成问答链路
* 消费 `retrieval` 返回的上下文，不直接操作向量库
* 组装 prompt / context / citations
* 调用 chat model 生成最终答案

这样可以把“检索能力”和“生成问答”长期分开维护，避免随着 RAG 策略演进把目录重新搅在一起。

---

## 8. `workflow` 模块

职责：

* 用 LangGraph 管理解析和索引任务流
* 支持 checkpoint
* 支持失败恢复
* 支持 HITL 审核节点

LangGraph 官方文档明确强调 durable execution、streaming、human-in-the-loop；对“收到路径或 URL 后经历多步处理”的任务流，这比普通同步函数链更适合。([LangChain Docs][8])

---

## 9. `storage` 模块

职责：

* 元数据库：SQLite，承载文档表、任务表、知识库表、DOC_CHUNKS 元信息表（可替换为 Postgres）
* 向量库：向量和可检索 metadata
* 不负责原始文件存储，只管理处理状态和索引结果

建议分开存，不要全塞向量库；原始文件默认由 `data/` 目录或外部 URL 提供。

---

# 四、项目文件结构

我建议你在当前仓库里直接按下面这个 `src/` 结构组织代码：

```text
ai-center-v4/
├── data/
├── doc/
├── src/
│   ├── main.py
│   ├── config/
│   │   ├── settings.py
│   │   ├── logging.py
│   │   └── constants.py
│   ├── api/
│   │   ├── deps.py
│   │   ├── routers/
│   │   │   ├── documents.py
│   │   │   ├── search.py
│   │   │   ├── rag.py
│   │   │   └── jobs.py
│   ├── schemas/
│   │   ├── document.py
│   │   ├── search.py
│   │   ├── rag.py
│   │   └── job.py
│   ├── ingestion/
│   │   ├── service.py
│   │   ├── dedup.py
│   │   ├── source_resolver.py
│   │   └── mime_detect.py
│   ├── processing/
│   │   ├── loaders/
│   │   │   ├── base.py
│   │   │   └── docling_loader.py
│   │   ├── normalize/            # 预留轻量标准化
│   │   │   ├── metadata.py
│   │   │   └── validators.py
│   │   └── chunking/             # 预留，第一阶段不实现
│   ├── embeddings/
│   │   ├── base.py
│   │   ├── factory.py
│   │   └── service.py
│   ├── indexing/
│   │   ├── service.py
│   │   ├── vector_store.py
│   │   └── upsert.py
│   ├── retrieval/
│   │   ├── service.py
│   │   ├── retriever_factory.py
│   │   ├── filters.py
│   │   ├── rerank.py
│   │   └── query_plan.py
│   ├── rag/
│   │   ├── service.py
│   │   ├── prompt_builder.py
│   │   └── answer_chain.py
│   ├── workflows/
│   │   ├── ingestion_graph.py
│   │   ├── reindex_graph.py
│   │   └── state.py
│   ├── repositories/
│   │   ├── document_repo.py
│   │   ├── chunk_repo.py
│   │   └── job_repo.py
│   ├── models/
│   │   ├── document.py
│   │   ├── chunk.py
│   │   └── job.py
│   ├── infra/
│   │   ├── db.py
│   │   ├── qdrant.py
│   │   └── queue.py
│   └── utils/
│       ├── hashing.py
│       ├── time.py
│       └── ids.py
├── tests/
│   ├── api/
│   ├── processing/
│   ├── indexing/
│   ├── retrieval/
│   └── rag/
├── scripts/
│   ├── init_collections.py
│   ├── reindex_all.py
│   └── backfill_metadata.py
├── migrations/
├── requirements.txt
├── Dockerfile
└── README.md
```

这个结构的核心思想是：**一级目录按业务域划分，域内再按 LangChain 链路细分能力**。`processing` 负责收敛文档处理相关子能力，`retrieval` 和 `rag` 分别负责“召回”与“生成”，这样后面扩展多解析器、多知识库、多种 RAG 策略时不容易乱。

---

# 五、核心调用链

## 1. 文档入库链路

```text
提交 `data/` 路径或 URL
→ ingestion 解析输入源
→ processing/loaders 路由解析器
→ 输出标准 DOC_CHUNKS
→ processing/normalize 轻量校验 + metadata 补全
→ embeddings 基于 DOC_CHUNKS 生成向量
→ indexing 写入向量库
→ repositories 写入文档状态 / DOC_CHUNKS 元数据
→ 返回 job 完成状态
```

这条链路完全贴合 LangChain 官方的知识库 / retrieval 基础链路。([LangChain Docs][6])

补充说明：

* 主链路不经过 `processing/chunking`
* 其他格式输出只作为兼容产物保留，供后续 `processing/chunking` 模块接入

---

## 2. 查询链路

```text
用户问题
→ retrieval 根据 query + metadata_filter 构造 retriever
→ retriever 执行向量检索 / hybrid 检索
→ rerank（可选）
→ rag 组装上下文
→ rag 走 2-Step RAG 生成答案
→ 返回答案 + 引用 chunk
```

LangChain 官方明确把 2-Step RAG 定义为单次生成前先检索的方式，适合 FAQ、文档机器人这类场景。你现在的文档子系统优先上这条就够了。([LangChain Docs][7])

---

# 六、实现思路

## 1. 先做“解析标准化”，不要先做“模型问答”

第一版最重要的不是 RAG 输出，而是把不同文件都统一成稳定的 `DOC_CHUNKS` + metadata 结构。
因为 LangChain 的上层检索、向量库、RAG，都是建立在这个标准输入上的。([LangChain Docs][1])

### 标准 `DOC_CHUNKS` 建议

每个解析结果统一成：

* `chunk_id`
* `text`
* `metadata.document_id`
* `metadata.file_name`
* `metadata.page`
* `metadata.section_title`
* `metadata.parser`
* `metadata.source_uri`
* `metadata.tenant_id`
* `metadata.knowledge_base_id`
* `metadata.chunk_type`
* `metadata.chunk_index`

---

## 3. 解析器要可插拔

`processing/loaders/base.py` 里定义统一接口：

```python
class ParsedOutput(TypedDict, total=False):
    doc_chunks: list[DocChunk]
    markdown: str
    text: str
    structured_json: dict
    documents: list[Document]

class BaseDocumentLoader(Protocol):
    def load(self, source: str) -> ParsedOutput: ...
```

当前阶段由 `processing/loaders/docling_loader.py` 直接实现这套接口即可。
以后如果你换成 MinerU、Marker、Azure OCR、阿里 OCR，再补 `router.py` 和对应 loader，也不改上层；同时也能保留不同格式输出，供后续 `processing/chunking` 或其他处理模块消费。

---

## 4. 任务流要异步

文档解析和索引构建不要挂在同步 HTTP 请求里。
应该是：

* API 收到路径或 URL 解析请求
* 创建 job
* 异步任务执行解析和索引
* 前端轮询 job 状态

这能避免大文件超时，也给 LangGraph 的 checkpoint/retry 留空间。LangGraph 的 durable execution 就很适合撑这类长任务。([LangChain Docs][8])

---

## 5. 向量库与元数据分离

不要把所有文档管理数据都塞进向量库。建议：

* **SQLite**：文档表、任务表、知识库表、chunk 元信息表（可替换为 Postgres）
* **Qdrant**：向量 + 检索 metadata

原始文件不由本服务存储，默认来自 `data/` 目录或外部 URL。本服务只保留处理状态、索引结果，以及按需导出的中间格式。

---

## 6. 检索接口建议

建议从第一阶段开始就把检索请求统一成带 filter 的结构，例如：

```json
{
  "query": "报销制度里差旅补贴标准是什么？",
  "top_k": 10,
  "metadata_filter": {
    "tenant_id": "t1",
    "knowledge_base_id": "kb_finance",
    "doc_type": "policy"
  }
}
```

这样 `metadata_filter` 可以在检索阶段直接下推到 Qdrant，而不是等召回后再在应用层二次过滤。

---

## 7. 第一阶段只上 2-Step RAG

LangChain retrieval 文档对三种模式的划分很清楚：
2-Step RAG 简单、可预测、快；Agentic RAG 灵活但延迟更不稳定。你的文档子系统第一阶段显然更适合前者。([LangChain Docs][7])

所以 `rag/answer_chain.py` 第一版只做：

* query embedding
* retriever build（支持 `metadata_filter`）
* retriever search
* optional rerank
* context assemble
* one-shot answer generation

别一开始就把 agent 拉进来。

---

# 八、第一版里最值得做的 5 个点

## 必做

1. **输入源去重**：按 SHA256 去重
2. **DOC_CHUNKS 可追溯**：每个 chunk 都能追到原文件、页码、章节
3. **异步任务状态**：queued / running / failed / finished
4. **metadata_filter 一等公民**：`/search` 和 `/rag/query` 第一版就支持 `tenant_id / knowledge_base_id / doc_type / page` 等过滤
5. **引用返回**：RAG 输出必须带 chunk 引用信息

---

# 九、我给你的最终推荐版

如果你现在就要开工，我建议你这样定：

**服务形态**

* 当前仓库内采用 `src/` 组织的文档处理子系统

**主栈**

* FastAPI
* LangChain
* LangGraph
* Docling
* Qdrant
* SQLite（可替换为 Postgres）

**模块边界**

* `api`
* `ingestion`
* `processing`
* `embeddings`
* `indexing`
* `retrieval`
* `rag`
* `workflows`
* `storage`

**第一阶段目标**

* 跑通 `data/` 路径 / URL 输入 → 解析 → `DOC_CHUNKS` 标准化 → 入库 → 检索 → 2-Step RAG 全链路

这套方案最大的好处是：**架构不重，但扩展口都留好了**。你后面无论接 OCR、接更多解析器、接多知识库、接 LangGraph agent，都不用推翻重来。

下一步我可以直接给你补一版：**数据库表设计 + API 设计 + 每个模块的核心类定义**。

[1]: https://docs.langchain.com/oss/python/integrations/document_loaders?utm_source=chatgpt.com "Document loader integrations - Docs by LangChain"
[2]: https://docs.langchain.com/oss/python/integrations/document_loaders/docling?utm_source=chatgpt.com "Docling integration - Docs by LangChain"
[3]: https://docs.langchain.com/oss/python/integrations/document_loaders/image?utm_source=chatgpt.com "Images integration - Docs by LangChain"
[4]: https://docs.langchain.com/oss/python/integrations/splitters?utm_source=chatgpt.com "Text splitter integrations - Docs by LangChain"
[5]: https://docs.langchain.com/oss/python/integrations/splitters/markdown_header_metadata_splitter?utm_source=chatgpt.com "Split markdown - text splitter integration"
[6]: https://docs.langchain.com/oss/python/langchain/knowledge-base?utm_source=chatgpt.com "Build a semantic search engine with LangChain"
[7]: https://docs.langchain.com/oss/python/langchain/retrieval?utm_source=chatgpt.com "Retrieval - Docs by LangChain"
[8]: https://docs.langchain.com/oss/python/langgraph/overview?utm_source=chatgpt.com "LangGraph overview - Docs by LangChain"
[9]: https://qdrant.tech/documentation/frameworks/langchain/ "Qdrant x LangChain integration"
