# 📚 Claude Code 知识库建设开源项目深度调研与落地验证

> 系统性调研基于 Claude Code 搭建知识库的优秀开源项目，通过源码分析深度挖掘底层技术方案，并以 Godot 引擎源码为实战对象进行知识库建设的落地验证。

---

## 🎯 项目目标

1. **检索发现** — 持续追踪 GitHub 上 Claude Code 知识库相关的优秀开源项目
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
│   ├── survey-plan.md         # 总调研规划表（待探索 / 探索中 / 已完成）
│   ├── yamadashy-repomix/     # Repomix 调研（⭐23,562 ✅已完成）
│   │   └── analysis.md        # 源码分析与技术方案
│   ├── mufeedvh-code2prompt/  # Code2Prompt 调研（⭐7,283 ✅已完成）
│   │   └── analysis.md        # 源码分析与技术方案
│   ├── sweepai-sweep/         # Sweep 调研（⭐7,710 ✅已完成）
│   │   └── analysis.md        # 源码分析与技术方案
│   └── lucasrosati-claude-code-memory-setup/  # Claude Code Memory 调研（⭐175 ✅已完成）
│       └── analysis.md        # 源码分析与技术方案
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
    └── github-search.py       # GitHub 项目检索脚本
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

### 探索项目列表

> 以下列表由定时任务自动更新，按 Star 数降序排列

| # | 项目 | ⭐ Stars | 描述 | 状态 | 调研文档 |
|---|------|---------|------|------|---------|
| 1 | [yamadashy/repomix](https://github.com/yamadashy/repomix) | 23,562 | 代码仓库打包为 AI 友好文件（MCP+AST压缩） | ✅已完成 | [分析报告](projects/yamadashy-repomix/analysis.md) |
| 2 | [sweepai/sweep](https://github.com/sweepai/sweep) | 7,710 | AI GitHub App 端到端自动化（向量+全文+依赖图检索） | ✅已完成 | [分析报告](projects/sweepai-sweep/analysis.md) |
| 3 | [mufeedvh/code2prompt](https://github.com/mufeedvh/code2prompt) | 7,283 | Rust 高性能代码打包工具（TUI+模板） | ✅已完成 | [分析报告](projects/mufeedvh-code2prompt/analysis.md) |
| 4 | [raphaelmansuy/code2prompt](https://github.com/raphaelmansuy/code2prompt) | 883 | Python 版代码打包工具 | ⏳待探索 | |
| 5 | [FlineDev/ContextKit](https://github.com/FlineDev/ContextKit) | 165 | Claude Code 上下文工程与规划系统 | ⏳待探索 | |
| 6 | [lucasrosati/claude-code-memory-setup](https://github.com/lucasrosati/claude-code-memory-setup) | 175 | Claude Code 记忆系统 (Obsidian+Graphify) | ✅已完成 | [分析报告](projects/lucasrosati-claude-code-memory-setup/analysis.md) |
| 7 | [AndersonBY/python-repomix](https://github.com/AndersonBY/python-repomix) | 153 | Python 版 Repomix | ⏳待探索 | |
| 8 | [nwiizo/cctx](https://github.com/nwiizo/cctx) | 142 | Claude Code 上下文管理器（Rust 多配置切换） | ⏳待探索 | |
| 9 | [S1LV4/th0th](https://github.com/S1LV4/th0th) | 132 | 代码语义搜索引擎（98% token 减少） | ⏳待探索 | |
| 10 | [Ataraxy-Labs/inspect](https://github.com/Ataraxy-Labs/inspect) | 121 | 基于图的代码审查工具 | ⏳待探索 | |
| 11 | [anrgct/autodev-codebase](https://github.com/anrgct/autodev-codebase) | 115 | 向量嵌入代码语义搜索（MCP） | ⏳待探索 | |
| 12 | [greptileai/greptile-vscode](https://github.com/greptileai/greptile-vscode) | 83 | Greptile VS Code 扩展（代码智能） | ⏳待探索 | |
| 13 | [Abinesh-L/claude-crusts](https://github.com/Abinesh-L/claude-crusts) | 67 | Claude Code 上下文窗口分析 | ⏳待探索 | |
| 14 | [brandondocusen/CntxtJS](https://github.com/brandondocusen/CntxtJS) | 63 | JS/TS 知识图谱优化 LLM 上下文 | ⏳待探索 | |
| 15 | [Thibault-Knobloch/codebase-intelligence](https://github.com/Thibault-Knobloch/codebase-intelligence) | 48 | 代码库索引+嵌入+NL 查询 | ⏳待探索 | |
| 16 | [opensesh/KARIMO](https://github.com/opensesh/KARIMO) | 30 | Claude Code 工程框架，Agent 编排 | ⏳待探索 | |
| 17 | [sdsrss/code-graph-mcp](https://github.com/sdsrss/code-graph-mcp) | 22 | AST 知识图谱 MCP 服务器 | ⏳待探索 | |
| 18 | [eersnington/diff0](https://github.com/eersnington/diff0) | 22 | AI 代码审查（开源 CodeRabbit/Greptile 替代） | ⏳待探索 | |
| 19 | [iM3SK/cc-aio-mon](https://github.com/iM3SK/cc-aio-mon) | 21 | Claude Code 实时终端监控 | ⏳待探索 | |

<details>
<summary>📊 查看完整统计</summary>

- 已发现项目：26
- ✅ 已完成调研：4（Repomix, Sweep, Code2Prompt, Claude Code Memory Setup）
- ⏳ 待探索：15
- 🚫 已排除：5
- 本轮新发现：6（ContextKit, cctx, Greptile VSCode, KARIMO, diff0, cc-aio-mon）
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
| 2026-04-16 | 🔍 第2轮调研：完成 Sweep（⭐7,710）和 Claude Code Memory Setup（⭐175）深度分析；新发现 6 个项目（ContextKit、cctx、Greptile VSCode、KARIMO、diff0、cc-aio-mon）；累计调研项目达 26 个 |
| 2026-04-16 | 🔍 首轮调研：完成 Repomix（⭐23,562）和 Code2Prompt（⭐7,283）深度分析；检索发现 20 个相关项目；更新调研规划表 |
| 2025-04-15 | 项目初始化，创建仓库结构与执行规范 |

---

## 📌 关键发现摘要

### Repomix（⭐23,562）— 推荐作为知识库基础工具
- **核心能力**：代码打包 + Tree-sitter AST 压缩（~70% token 减少）+ MCP 集成
- **推荐理由**：原生 MCP Server 支持，可直接集成 Claude Code；17 种语言的 AST 压缩；Skill 自动生成
- **局限**：无语义搜索（RAG）能力，无增量更新

### Sweep（⭐7,710）— 搜索管线设计精良的 AI GitHub App
- **核心能力**：Issue→搜索→规划→修改→PR 端到端自动化；多查询扩展+向量检索+Tantivy全文+Cohere/LLM重排序+NetworkX依赖图修剪
- **推荐理由**：搜索管线设计精良，多路检索融合策略值得借鉴；支持 OpenAI+Anthropic 双后端
- **局限**：项目已转型 JetBrains 插件方向；依赖链重（80+包、Redis+MongoDB）；部署复杂度高

### Code2Prompt（⭐7,283）— 精确上下文控制工具
- **核心能力**：Rust 高性能 + TUI 交互式文件选择 + Handlebars 模板
- **推荐理由**：交互式精确控制上下文；Python SDK 便于自动化；特殊文件格式支持（CSV/Notebook）
- **局限**：无 MCP 支持，无代码压缩，无安全检查

### Claude Code Memory Setup（⭐175）— Obsidian + Graphify 记忆系统
- **核心能力**：Obsidian Zettelkasten 持久化声明式记忆 + Graphify tree-sitter AST 知识图谱 + 三层查询规则
- **推荐理由**：Token 节省显著（71.5x~499x）；AST 模式零 API Token 消耗；完全本地化隐私安全
- **局限**：纯文档项目无可执行代码；无自动化安装脚本门槛高；脚本仅为伪代码级别

---

> 🤖 本项目调研由 Hermes Agent 自动化执行，定时检索 → 深度分析 → 落地验证 → 文档推送