# 📚 Claude Code 知识库建设开源项目深度调研与落地验证

> 系统性调研基于 Claude Code 搭建知识库的优秀开源项目，通过源码分析深度挖掘底层技术方案，并以 Godot 引擎源码为实战对象进行知识库建设的落地验证。

---

## 🎯 项目目标

1. **检索发现** — 持续追踪 GitHub 上 Claude Code 知识库相关的优秀开源项目（≥5000 Star）
2. **深度调研** — 通过源码分析，深入理解每个项目的底层技术方案、优缺点、最佳应用场景
3. **落地验证** — 使用 Godot 引擎源码（~200万行 C++）作为真实场景，验证知识库建设的实际效果
4. **Benchmark** — 设计可量化的评测方案，对比有/无知识库对 AI 编码能力的实际差异
5. **文档沉淀** — 形成完整的调研分析文档，包括安装部署、踩坑记录、解决方案、效果验证

---

## 📂 项目结构

```
knowledge-base-research/
├── README.md                  # 本文件 — 项目索引与进度追踪
├── projects/                  # 各开源项目深度调研文档
│   ├── survey-plan.md         # 总调研规划表（按 Star 排序）
│   ├── thedotmack-claude-mem/ # claude-mem 调研（⭐58,089 ✅已完成）⭐NEW
│   │   └── analysis.md        # 源码分析与技术方案
│   ├── BloopAI-bloop/         # Bloop 调研（⭐9,508 ✅已完成）⭐NEW
│   │   └── analysis.md        # 源码分析与技术方案
│   ├── yamadashy-repomix/     # Repomix 调研（⭐23,562 ✅已完成）
│   │   └── analysis.md
│   ├── mufeedvh-code2prompt/  # Code2Prompt 调研（⭐7,283 ✅已完成）
│   │   └── analysis.md
│   ├── sweepai-sweep/         # Sweep 调研（⭐7,710 ✅已完成）
│   │   └── analysis.md
│   └── lucasrosati-claude-code-memory-setup/  # Memory Setup（⭐175 ✅已完成）
│       └── analysis.md
├── godot-verification/        # Godot 源码知识库落地验证
│   ├── setup.md               # 安装部署指南
│   ├── pitfalls.md            # 踩坑记录与解决方案
│   ├── results.md             # 知识库效果验证结果
│   └── reports/               # 各阶段验证报告
├── benchmark/                 # 效果评测 Benchmark
│   ├── design.md              # Benchmark 设计方案
│   ├── dataset/               # 测试数据集
│   └── results/               # 评测结果
├── specs/                     # 执行规范
│   ├── execution-standard.md  # 项目执行规范
│   └── lessons-learned.md     # 经验教训总结
└── scripts/                   # 自动化脚本
```

---

## 📋 调研规划表

### 状态说明
| 图标 | 状态 | 含义 |
|------|------|------|
| ⏳ | 待探索 | 已发现，尚未开始深度调研 |
| 🔍 | 探索中 | 正在进行源码分析 |
| ✅ | 已完成 | 调研报告已完成 |
| 🚫 | 已排除 | 不符合要求，已跳过 |

### 核心项目列表（≥5000 Star）

> 以下列表由定时任务自动更新，按 Star 数降序排列

| # | 项目 | ⭐ Stars | 描述 | 状态 | 调研文档 |
|---|------|---------|------|------|---------|
| 1 | [microsoft/markitdown](https://github.com/microsoft/markitdown) | 109,647 | 文档转 Markdown 工具 | ⏳待探索 | |
| 2 | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | 58,089 | Claude Code 记忆插件（RAG+MCP） | ✅已完成 | [报告](projects/thedotmack-claude-mem/analysis.md) |
| 3 | [gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done) | 53,638 | Context Engineering for Claude Code | ⏳待探索 | |
| 4 | [mem0ai/mem0](https://github.com/mem0ai/mem0) | 53,162 | AI Agent 通用记忆层 | ⏳待探索 | |
| 5 | [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) | 44,207 | Karpathy 风格 Claude Code Skills | ⏳待探索 | |
| 6 | [milvus-io/milvus](https://github.com/milvus-io/milvus) | 43,821 | 云原生向量数据库 | ⏳待探索 | |
| 7 | [qdrant/qdrant](https://github.com/qdrant/qdrant) | 30,365 | Rust 向量搜索引擎 | ⏳待探索 | |
| 8 | [chroma-core/chroma](https://github.com/chroma-core/chroma) | 27,456 | AI 原生嵌入数据库 | ⏳待探索 | |
| 9 | [yamadashy/repomix](https://github.com/yamadashy/repomix) | 23,562 | 代码打包（MCP+AST压缩） | ✅已完成 | [报告](projects/yamadashy-repomix/analysis.md) |
| 10 | [jarrodwatts/claude-hud](https://github.com/jarrodwatts/claude-hud) | 19,447 | Claude Code HUD 界面 | ⏳待探索 | |
| 11 | [coleam00/Archon](https://github.com/coleam00/Archon) | 18,252 | AI Agent 架构师 | ⏳待探索 | |
| 12 | [weaviate/weaviate](https://github.com/weaviate/weaviate) | 16,012 | Go 向量数据库 | ⏳待探索 | |
| 13 | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 15,992 | AI Agent Skills 集合 | ⏳待探索 | |
| 14 | [coleam00/context-engineering-intro](https://github.com/coleam00/context-engineering-intro) | 13,168 | Context Engineering 入门 | ⏳待探索 | |
| 15 | [sourcegraph/sourcegraph-public-snapshot](https://github.com/sourcegraph/sourcegraph-public-snapshot) | 10,266 | 代码搜索平台（公开快照） | ⏳待探索 | |
| 16 | [lancedb/lancedb](https://github.com/lancedb/lancedb) | 9,960 | 嵌入式向量数据库（Rust） | ⏳待探索 | |
| 17 | [BloopAI/bloop](https://github.com/BloopAI/bloop) | 9,508 | Rust 代码搜索引擎（已归档） | ✅已完成 | [报告](projects/BloopAI-bloop/analysis.md) |
| 18 | [sweepai/sweep](https://github.com/sweepai/sweep) | 7,710 | AI GitHub App 端到端 | ✅已完成 | [报告](projects/sweepai-sweep/analysis.md) |
| 19 | [mksglu/context-mode](https://github.com/mksglu/context-mode) | 7,329 | Claude Code 上下文模式 | ⏳待探索 | |
| 20 | [mufeedvh/code2prompt](https://github.com/mufeedvh/code2prompt) | 7,283 | Rust 高性能代码打包工具 | ✅已完成 | [报告](projects/mufeedvh-code2prompt/analysis.md) |

<details>
<summary>📊 查看完整统计</summary>

- 已发现项目（≥5000 Star）：20
- ✅ 已完成深度调研：6（claude-mem, bloop, repomix, sweep, code2prompt, memory-setup）
- ⏳ 待探索：14
- 🆕 本轮新发现：16
</details>

---

## 📊 Benchmark 概览

> 知识库效果验证评测：对比有/无知识库时 AI 在 Godot 代码理解与生成任务上的表现

详细方案见 [benchmark/design.md](benchmark/design.md)

| 评测维度 | 无知识库 | 有知识库 | 提升 |
|----------|---------|---------|------|
| *待评测...* | — | — | — |

---

## 🔧 执行规范

详细规范见 [specs/execution-standard.md](specs/execution-standard.md)

---

## 📅 更新日志

| 日期 | 更新内容 |
|------|---------|
| 2026-04-16 | 🔍 **第3轮调研**：完成 **claude-mem**（⭐58,089）和 **Bloop**（⭐9,508）深度源码分析；通过 GitHub Trending + API 搜索新发现 16 个 ≥5000 Star 项目；重大发现：claude-mem 是目前 Claude Code 知识库建设的最高水平开源项目 |
| 2026-04-16 | 🔍 第2轮调研：完成 Sweep（⭐7,710）和 Claude Code Memory Setup（⭐175）深度分析 |
| 2026-04-16 | 🔍 首轮调研：完成 Repomix（⭐23,562）和 Code2Prompt（⭐7,283）深度分析 |
| 2025-04-15 | 项目初始化，创建仓库结构与执行规范 |

---

## 📌 关键发现摘要

### 🏆 claude-mem（⭐58,089）— ⭐⭐⭐⭐⭐ 强烈推荐
- **核心能力**：自动捕获所有工具调用 → AI 压缩为结构化观察 → SQLite+ChromaDB 双存储 → 三层渐进式披露检索（search→timeline→get_observations）
- **架构亮点**：两进程 fire-and-forget 设计（不阻塞 IDE）；Observer-only Agent（只分析不修改）；粒度向量化（每字段单独索引）；WAL SQLite + FTS5 + ChromaDB 三重搜索
- **Token 效率**：三层方案比传统 RAG 节省 50-75% Token
- **推荐理由**：**目前 Claude Code 知识库建设的标杆项目**，原生 MCP + Hooks 集成，开箱即用
- **局限**：依赖 Bun 运行时 + 可选 ChromaDB；AI 压缩消耗 API Token

### Bloop（⭐9,508）— ⭐⭐⭐ 架构参考
- **核心能力**：Rust 代码搜索引擎（Tantivy 全文 + Qdrant 向量 + GPT-4 问答）
- **架构亮点**：Tree-sitter 感知分块（50-256 tokens）；RRF 混合搜索合并（语义+词法）；HyDE 假设文档嵌入；正则→三元组规划；三级缓存（blake3 哈希）
- **推荐理由**：混合搜索架构的教科书级实现，Tree-sitter 分块和 RRF 合并值得借鉴
- **局限**：已归档；依赖重（Qdrant+ONNX+GPT-4）；通用嵌入模型（非代码专用）

### Repomix（⭐23,562）— ⭐⭐⭐⭐ 推荐作为基础工具
- **核心能力**：代码打包 + Tree-sitter AST 压缩（~70% token 减少）+ MCP 集成
- **推荐理由**：原生 MCP Server 支持；17 种语言 AST 压缩；Skill 自动生成
- **局限**：无语义搜索（RAG）能力，无增量更新

### Sweep（⭐7,710）— ⭐⭐⭐ 搜索管线参考
- **核心能力**：Issue→搜索→规划→修改→PR 端到端自动化
- **推荐理由**：多路检索融合策略（向量+全文+重排序+依赖图修剪）值得借鉴
- **局限**：已转型方向；部署复杂

---

## 🏗️ 知识库建设架构共识（基于调研积累）

基于 6 个项目的深度分析，我们总结出 Claude Code 知识库建设的最佳实践架构：

```
┌─────────────────────────────────────────────────────┐
│  知识捕获层                                         │
│  Claude Code Hooks → 隐私过滤 → AI 压缩 → 结构化存储 │
│  参考: claude-mem 的 Observer-only Agent             │
├─────────────────────────────────────────────────────┤
│  存储层                                             │
│  SQLite (结构化+FTS5) + Vector DB (语义搜索)         │
│  参考: claude-mem 双存储 + bloop 三级缓存            │
├─────────────────────────────────────────────────────┤
│  检索层                                             │
│  三层渐进式披露 + 混合搜索 (BM25 + Vector + RRF)     │
│  参考: claude-mem 三层 + bloop RRF + HyDE            │
├─────────────────────────────────────────────────────┤
│  代码理解层                                         │
│  Tree-sitter AST 解析 + 符号提取 + 语义分块          │
│  参考: bloop Tree-sitter 感知分块 + ScopeGraph       │
├─────────────────────────────────────────────────────┤
│  集成层                                             │
│  MCP Server (工具) + Hooks (生命周期) + Context 注入  │
│  参考: claude-mem 完整 Claude Code 集成              │
└─────────────────────────────────────────────────────┘
```

---

> 🤖 本项目调研由 Hermes Agent 自动化执行，定时检索 → 深度分析 → 落地验证 → 文档推送
