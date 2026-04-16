# 📋 知识库开源项目调研规划表

> 持续更新的调研规划，由定时任务自动维护
> ⚠️ **最低 Star 门槛：5000**，低于 5000 star 的项目一律不入表

---

## 检索关键词

- `knowledge base`, `RAG`, `code intelligence`, `code search`
- `AI coding`, `Claude Code`, `codebase indexing`
- `semantic search`, `vector search`, `code embedding`
- `MCP server`, `context management`
- `claude code memory`, `claude code context`
- `codebase understanding tool`, `code RAG knowledge`
- `code semantic search`, `code embedding search`
- `code documentation AI agent`, `codebase context LLM`
- `greptile`, `code knowledge graph LLM`

---

## 已发现项目（≥5000 Star）

> 按 Star 数降序排列，状态：⏳待探索 | 🔍探索中 | ✅已完成 | 🚫已排除

| # | 项目 | ⭐ Stars | 描述 | 发现时间 | 状态 | 调研文档 |
|---|------|---------|------|---------|------|---------|
| 1 | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | 58,089 | Claude Code 记忆插件（ChromaDB+SQLite+RAG+MCP） | 2026-04-16 | ✅已完成 | [分析报告](thedotmack-claude-mem/analysis.md) |
| 2 | [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) | 44,207 | Karpathy 风格的 Claude Code Skills 集合 | 2026-04-16 | ⏳待探索 | |
| 3 | [milvus-io/milvus](https://github.com/milvus-io/milvus) | 43,821 | 云原生向量数据库（Go+C++） | 2026-04-16 | ⏳待探索 | |
| 4 | [yamadashy/repomix](https://github.com/yamadashy/repomix) | 23,562 | 代码仓库打包为 AI 友好文件（MCP+AST压缩） | 2026-04-16 | ✅已完成 | [分析报告](yamadashy-repomix/analysis.md) |
| 5 | [jarrodwatts/claude-hud](https://github.com/jarrodwatts/claude-hud) | 19,447 | Claude Code HUD 界面 | 2026-04-16 | ⏳待探索 | |
| 6 | [coleam00/Archon](https://github.com/coleam00/Archon) | 18,252 | AI Agent 架构师 | 2026-04-16 | ⏳待探索 | |
| 7 | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 15,992 | AI Agent Skills 集合 | 2026-04-16 | ⏳待探索 | |
| 8 | [weaviate/weaviate](https://github.com/weaviate/weaviate) | 16,012 | 向量数据库（Go） | 2026-04-16 | ⏳待探索 | |
| 9 | [coleam00/context-engineering-intro](https://github.com/coleam00/context-engineering-intro) | 13,168 | Context Engineering 入门 | 2026-04-16 | ⏳待探索 | |
| 10 | [sourcegraph/sourcegraph-public-snapshot](https://github.com/sourcegraph/sourcegraph-public-snapshot) | 10,266 | Sourcegraph 代码搜索平台（公开快照） | 2026-04-16 | ⏳待探索 | |
| 11 | [lancedb/lancedb](https://github.com/lancedb/lancedb) | 9,960 | LanceDB 嵌入式向量数据库（Rust） | 2026-04-16 | ⏳待探索 | |
| 12 | [BloopAI/bloop](https://github.com/BloopAI/bloop) | 9,508 | Rust 代码搜索引擎（Tantivy+Qdrant+GPT-4） | 2026-04-16 | ✅已完成 | [分析报告](BloopAI-bloop/analysis.md) |
| 13 | [sweepai/sweep](https://github.com/sweepai/sweep) | 7,710 | AI GitHub App 端到端自动化 | 2026-04-16 | ✅已完成 | [分析报告](sweepai-sweep/analysis.md) |
| 14 | [mufeedvh/code2prompt](https://github.com/mufeedvh/code2prompt) | 7,283 | Rust 高性能代码打包工具 | 2026-04-16 | ✅已完成 | [分析报告](mufeedvh-code2prompt/analysis.md) |
| 15 | [mksglu/context-mode](https://github.com/mksglu/context-mode) | 7,329 | Claude Code 上下文模式 | 2026-04-16 | ⏳待探索 | |
| 16 | [chroma-core/chroma](https://github.com/chroma-core/chroma) | 27,456 | AI 原生嵌入数据库（Rust+Python） | 2026-04-16 | ⏳待探索 | |
| 17 | [qdrant/qdrant](https://github.com/qdrant/qdrant) | 30,365 | 向量相似度搜索引擎（Rust） | 2026-04-16 | ⏳待探索 | |
| 18 | [gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done) | 53,638 | Claude Code Context Engineering 工具 | 2026-04-16 | ⏳待探索 | |
| 19 | [mem0ai/mem0](https://github.com/mem0ai/mem0) | 53,162 | AI Agent 通用记忆层 | 2026-04-16 | ⏳待探索 | |
| 20 | [microsoft/markitdown](https://github.com/microsoft/markitdown) | 109,647 | 微软文档转 Markdown 工具 | 2026-04-16 | ⏳待探索 | |

---

## 已发现项目（<5000 Star，仅供参考）

> 以下项目 Star 数低于 5000 门槛，仅做记录，不纳入正式调研

| 项目 | ⭐ Stars | 描述 | 状态 |
|------|---------|------|------|
| lucasrosati/claude-code-memory-setup | 175 | Obsidian + Graphify 记忆系统 | ✅已完成（早期调研） |
| raphaelmansuy/code2prompt | 883 | Python 版代码打包工具 | ⏳待探索 |
| FlineDev/ContextKit | 165 | Claude Code 上下文工程 | ⏳待探索 |
| nwiizo/cctx | 142 | Claude Code 上下文管理器 | ⏳待探索 |
| S1LV4/th0th | 132 | 代码语义搜索引擎 | ⏳待探索 |
| anrgct/autodev-codebase | 115 | 向量嵌入代码语义搜索（MCP） | ⏳待探索 |

---

## 调研排期

> 每轮定时任务按优先级选取项目进行深度调研

| 轮次 | 项目 | 开始时间 | 完成时间 | 备注 |
|------|------|---------|---------|------|
| 第1轮 | yamadashy/repomix | 2026-04-16 | 2026-04-16 | ⭐23,562 代码打包工具，MCP 支持 |
| 第1轮 | mufeedvh/code2prompt | 2026-04-16 | 2026-04-16 | ⭐7,283 Rust 高性能打包工具 |
| 第2轮 | sweepai/sweep | 2026-04-16 | 2026-04-16 | ⭐7,710 AI GitHub App |
| 第2轮 | lucasrosati/claude-code-memory-setup | 2026-04-16 | 2026-04-16 | ⭐175 Obsidian 记忆系统 |
| **第3轮** | **thedotmack/claude-mem** | **2026-04-16** | **2026-04-16** | **⭐58,089 Claude Code 记忆插件，三层渐进式披露** |
| **第3轮** | **BloopAI/bloop** | **2026-04-16** | **2026-04-16** | **⭐9,508 Rust 代码搜索引擎，混合搜索** |
| 第4轮 | 待定（优先: milvus-io/milvus 或 chroma-core/chroma） | - | - | 向量数据库对比 |

---

## 统计

- 已发现项目（≥5000 Star）：20
- 已完成深度调研：6（repomix, code2prompt, sweep, claude-code-memory-setup, claude-mem, bloop）
- 待探索（≥5000 Star）：14
- 本轮新发现（≥5000 Star）：16（claude-mem, gsd-build, mem0, forrestchang/skills, milvus, qdrant, chroma, claude-hud, Archon, agent-skills, weaviate, context-engineering-intro, sourcegraph, lancedb, bloop, markitdown）

---

## 项目分类

### 🔥 知识库/记忆系统（核心目标）
| 项目 | Stars | 特点 |
|------|-------|------|
| thedotmack/claude-mem | 58,089 | **最佳** — Claude Code 原生知识库，三层渐进式披露 |
| mem0ai/mem0 | 53,162 | 通用 AI 记忆层，多 provider |
| gsd-build/get-shit-done | 53,638 | Context Engineering for Claude Code |

### 🔍 代码搜索引擎
| 项目 | Stars | 特点 |
|------|-------|------|
| sourcegraph/sourcegraph-public-snapshot | 10,266 | 最成熟的代码搜索平台 |
| BloopAI/bloop | 9,508 | Rust 混合搜索（已归档） |

### 🗄️ 向量数据库
| 项目 | Stars | 特点 |
|------|-------|------|
| milvus-io/milvus | 43,821 | 云原生，Go+C++，可扩展 |
| qdrant/qdrant | 30,365 | Rust，高性能 |
| chroma-core/chroma | 27,456 | AI 原生，Python 友好 |
| weaviate/weaviate | 16,012 | Go，GraphQL API |
| lancedb/lancedb | 9,960 | Rust，嵌入式，Lance 格式 |

### 📦 代码打包/上下文工具
| 项目 | Stars | 特点 |
|------|-------|------|
| yamadashy/repomix | 23,562 | MCP 集成，AST 压缩 |
| mufeedvh/code2prompt | 7,283 | Rust 高性能，TUI |
| microsoft/markitdown | 109,647 | 文档转 Markdown |
