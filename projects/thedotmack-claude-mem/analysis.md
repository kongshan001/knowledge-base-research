# 🔍 claude-mem 深度源码分析报告

> **项目**: [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem)
> **Star**: ⭐58,089 | **语言**: TypeScript | **协议**: AGPL-3.0
> **版本**: 12.1.5 | **分析日期**: 2026-04-16
> **推荐等级**: ⭐⭐⭐⭐⭐（强烈推荐 — Claude Code 知识库建设的标杆项目）

---

## 一、项目概述

claude-mem 是一个 Claude Code 插件，自动捕获编码会话中的所有工具调用（文件读取、代码编辑、命令执行等），通过 AI 压缩为结构化观察记录，存储到本地 SQLite + ChromaDB 双存储中，并在后续会话中通过 MCP 工具实现渐进式上下文检索。

**核心理念**: Context Engineering — 找到最小的高信号 token 集合，最大化 AI 编码的期望结果。

---

## 二、系统架构

### 2.1 核心组件（6 层）

```
┌─────────────────────────────────────────────────┐
│  Claude Code Hooks (5 个生命周期钩子)            │
│  SessionStart → UserPromptSubmit → PostToolUse  │
│  → Stop → SessionEnd                            │
├─────────────────────────────────────────────────┤
│  Worker Service (Express.js HTTP, 端口 37777)   │
│  22+ REST API 端点 + SSE 实时推送                │
├─────────────────────────────────────────────────┤
│  SDK Agent / Gemini Agent (AI 压缩引擎)          │
│  Claude Agent SDK / Gemini REST API              │
├─────────────────────────────────────────────────┤
│  Database Layer (SQLite WAL + FTS5 + ChromaDB)   │
│  双存储：结构化 + 向量语义                        │
├─────────────────────────────────────────────────┤
│  MCP Server (4 个工具, stdio 传输)               │
│  __IMPORTANT / search / timeline / get_observations │
├─────────────────────────────────────────────────┤
│  Viewer UI (React Web 界面)                      │
│  localhost:37777 实时观察                         │
└─────────────────────────────────────────────────┘
```

### 2.2 两进程架构

```
Extension Process (IDE 层)
    │ fire-and-forget HTTP (2s 超时)
    ▼
Worker Process (独立 Bun 进程)
    │ Claude Agent SDK / Gemini API
    ▼
SQLite + ChromaDB
```

**设计原则**: 钩子层绝不阻塞 IDE（2s 超时 fire-and-forget），Worker 异步处理 AI 压缩。

---

## 三、知识库建设流程（完整数据流）

### 3.1 捕获阶段

```
Claude Code Session
    ↓ (PostToolUse hook)
save-hook.js (stdin: JSON)
    ↓ 隐私标签剥离 (<private>, <claude-mem-context>)
    ↓ Skip List 过滤 (TodoWrite, AskUserQuestion, etc.)
    ↓ fire-and-forget POST /api/sessions/observations
Worker Service
    ↓ 队列排队 (event-driven, 非轮询)
    ↓ SDK Agent / Gemini Agent 处理
    ↓ XML 格式响应解析
SQLite (observations 表) + ChromaDB (向量文档)
```

### 3.2 AI 压缩引擎

**SDK Agent**（使用 `@anthropic-ai/claude-agent-sdk`）:

1. **初始化 Prompt**: 系统身份 + 观察者角色 + 空间感知 + XML 输出格式模板
2. **观察 Prompt**: 
   ```xml
   <observed_from_primary_session>
     <what_happened>{tool_name}</what_happened>
     <occurred_at>{timestamp}</occurred_at>
     <parameters>{tool_input JSON}</parameters>
     <outcome>{tool_output JSON}</outcome>
   </observed_from_primary_session>
   ```
3. **XML 响应解析**: 提取 `type`, `title`, `subtitle`, `narrative`, `facts[]`, `concepts[]`, `files_read[]`, `files_modified[]`

**关键设计**: Observer-only 模式 — Agent 禁止执行任何工具（Bash, Read, Write 等均在 `disallowedTools` 列表中），只分析不修改。

### 3.3 存储架构

#### SQLite（主存储）

| 表名 | 用途 | 核心字段 |
|------|------|---------|
| `sdk_sessions` | 会话跟踪 | sdk_session_id, claude_session_id, project, status |
| `observations` | 结构化观察 | title, subtitle, narrative, facts(JSON), concepts(JSON), type, files_read(JSON), files_modified(JSON) |
| `session_summaries` | AI 生成摘要 | request, investigated, learned, completed, next_steps |
| `user_prompts` | 原始用户提示 | prompt_text |
| `pending_messages` | 处理队列 | 异步处理队列 |

#### FTS5 虚拟表（全文搜索）

- `observations_fts` — 索引 title, subtitle, narrative, text, facts, concepts
- `session_summaries_fts` — 索引 request, investigated, learned, completed, next_steps
- `user_prompts_fts` — 索引 prompt_text
- **自动同步触发器**: AFTER INSERT/UPDATE/DELETE 自动更新 FTS5

#### ChromaDB（向量语义搜索）

- 集合命名: `cm__{sanitized_project_name}`
- **粒度向量化策略**: 每个语义字段单独作为一份文档
  - 观察: `obs_{id}_narrative`, `obs_{id}_text`, `obs_{id}_fact_{index}`
  - 摘要: `summary_{id}_request`, `summary_{id}_learned`, `summary_{id}_completed` 等
  - 用户提示: `prompt_{id}` (单文档)
- 嵌入模型: ChromaDB 内置默认模型（项目不直接管理嵌入，消除 ONNX/WASM 依赖）

### 3.4 PRAGMA 优化配置

```sql
journal_mode = WAL          -- 并发读写
synchronous = NORMAL        -- 性能平衡
foreign_keys = ON           -- 数据完整性
temp_store = memory         -- 临时表内存
mmap_size = 268435456       -- 256MB 内存映射
cache_size = 10000          -- 页缓存
```

---

## 四、搜索策略架构

### 4.1 三层渐进式披露（Progressive Disclosure）

```
┌───────────────────────────────────────────────────────┐
│ Layer 1: search (索引层)                               │
│ GET /api/search → FTS5 全文搜索                        │
│ 成本: ~50-100 tokens/结果                              │
│ 目的: 快速浏览、过滤相关 ID                             │
├───────────────────────────────────────────────────────┤
│ Layer 2: timeline (上下文层)                           │
│ GET /api/timeline → 时间线上下文                        │
│ 成本: 可变                                              │
│ 目的: 锚点观察周围的故事线                               │
├───────────────────────────────────────────────────────┤
│ Layer 3: get_observations (详情层)                     │
│ POST /api/observations/batch → 完整详情                │
│ 成本: ~500-1000 tokens/观察                             │
│ 目的: 验证后的深度查看                                   │
└───────────────────────────────────────────────────────┘
```

**Token 效率对比**:
- 传统 RAG: 20 观察 × ~1,000 tokens = 10-20K tokens（10% 相关性 = 18K 浪费）
- 三层方案: search(2K) + get_observations(3 ID, 3K) = ~5K tokens → **50-75% 节省**

### 4.2 搜索策略模式（Strategy Pattern）

```
SearchOrchestrator
    ├── ChromaSearchStrategy  — 向量语义搜索
    │   └── ChromaDB query → 90天新近过滤 → doc_type分类 → SQLite水合
    ├── SQLiteSearchStrategy  — FTS5全文搜索
    │   └── SessionSearch FTS5 查询
    └── HybridSearchStrategy  — 混合搜索
        └── SQLite元数据过滤 ∩ Chroma语义排序 → 交集保留排名
```

**决策树**:
1. 无查询文本 → SQLite 纯过滤
2. 有查询文本 + Chroma 可用 → Chroma 语义搜索
3. Chroma 失败 → SQLite 降级（丢弃查询文本，纯过滤）
4. 无 Chroma → 返回空（语义查询不可能）

**混合搜索流程** (`findByConcept`, `findByType`, `findByFile`):
1. SQLite 元数据过滤 → 获取匹配 ID 集合
2. Chroma 语义排序 → 对 ID 按相关性排序
3. 交集 → 仅保留同时满足元数据和语义的 ID，保持 Chroma 排名顺序
4. SQLite 水合 → 按 Chroma 排名顺序获取完整记录

---

## 五、Claude Code 集成方式

### 5.1 Hooks 集成（5 个生命周期阶段）

| 阶段 | Hook | 核心操作 |
|------|------|---------|
| SessionStart | context-hook.js | 启动 Worker，注入前 50 条观察作为上下文 |
| UserPromptSubmit | new-hook.js | 创建/更新会话，保存原始提示到 FTS5 |
| PostToolUse | save-hook.js | 捕获工具调用，隐私剥离，异步 AI 压缩 |
| Stop | summary-hook.js | 读取 JSONL 转录，AI 生成结构化摘要 |
| SessionEnd | cleanup-hook.js | 标记会话完成，SSE 广播通知 |

### 5.2 MCP 工具集成

4 个 MCP 工具（stdio 传输）:
1. `__IMPORTANT` — 工作流文档（强制渐进式披露）
2. `search` — 全文搜索（返回紧凑索引 + ID）
3. `timeline` — 时间线上下文
4. `get_observations` — 批量获取完整详情

### 5.3 上下文注入

SessionStart 时通过 `additionalContext` 静默注入（Claude Code 2.1.0+）:
- 最近 50 条观察的结构化摘要
- Token 经济学计算（总 token 数、覆盖率）
- 项目上下文自动检测

---

## 六、高级特性

### 6.1 隐私保护

- **双层标签系统**: `<private>`（用户级）+ `<claude-mem-context>`（系统级，防止递归）
- **边缘处理**: Hook 层剥离标签后才发送到 Worker
- **ReDoS 防护**: 最多处理 100 个标签
- **纵深防御**: Worker 层二次剥离

### 6.2 多 AI Provider 支持

| Provider | 用途 | 配置 |
|----------|------|------|
| Claude (Agent SDK) | 默认压缩引擎 | `CLAUDE_MEM_MODEL`: haiku/sonnet/opus |
| Gemini | 替代压缩引擎 | `CLAUDE_MEM_GEMINI_API_KEY` |
| OpenRouter | 第三方路由 | `CLAUDE_MEM_OPENROUTER_KEY` |

Gemini Agent 特性:
- 多轮对话 REST API
- 速率限制（5-30 RPM per model）
- 上下文截断（滑动窗口，最新 20 条消息）
- 自动降级回 Claude SDK

### 6.3 Mode 系统

支持 30+ 编程语言的模式配置，每种模式定义:
- 观察类型（如 code 模式: decision, bugfix, feature, refactor, discovery, change）
- 输出语言
- 专注领域

### 6.4 Knowledge Agent (语料库系统)

- `CorpusBuilder`: 从搜索结果构建结构化语料
- `KnowledgeAgent`: 使用 Claude Agent SDK 进行语料库 Q&A
- `CorpusStore`: 文件持久化到 `~/.claude-mem/corpora/{name}.corpus.json`

### 6.5 多平台支持

支持 12+ AI 编码平台:
- Claude Code, Cursor, Windsurf, Gemini CLI, OpenCode, OpenClaw, Codex CLI, Zed

---

## 七、优缺点分析

### ✅ 优点

1. **架构精良**: 两进程 + fire-and-forget 设计，不阻塞 IDE
2. **双存储策略**: SQLite（结构化）+ ChromaDB（语义），可独立降级
3. **三层渐进式披露**: 结构性地减少 token 浪费（50-75% 节省）
4. **粒度向量化**: 每个语义字段单独索引，提高检索精度
5. **隐私优先**: 双层标签 + 边缘处理 + 纵深防御
6. **完全本地化**: 所有数据存储在 `~/.claude-mem/`，不上传云端
7. **Observer-only Agent**: AI 压缩引擎只分析不修改，安全可控
8. **丰富的集成**: Hooks + MCP + 多平台支持
9. **事件驱动队列**: 零延迟通知，非轮询
10. **WAL 模式 SQLite**: 支持并发读写

### ❌ 缺点

1. **依赖链重**: 需要 Bun 运行时 + 可选 ChromaDB (Python/uv)
2. **Token 消耗**: AI 压缩引擎本身消耗 API Token（每次观察都要调用 Claude）
3. **嵌入式向量模型**: 依赖 ChromaDB 默认模型，不可自定义
4. **单项目隔离**: 项目间知识不共享（按 project 字段隔离）
5. **无增量 AST 感知**: 不理解代码结构变化，只记录工具调用
6. **ChromaDB 运维**: 需要管理 Python 环境和 Chroma 进程

---

## 八、与 Claude Code 知识库建设的关系

### 8.1 直接可用性

**高度直接可用** — claude-mem 本身就是 Claude Code 的知识库:
- ✅ 原生 MCP 集成
- ✅ 自动上下文注入
- ✅ 会话间知识持久化
- ✅ 多种搜索策略
- ✅ 隐私保护

### 8.2 架构借鉴价值

| 模式 | 借鉴价值 |
|------|---------|
| 三层渐进式披露 | ⭐⭐⭐⭐⭐ 任何知识库都应采用的检索范式 |
| 双存储（SQL + Vector） | ⭐⭐⭐⭐⭐ 结构化 + 语义互补 |
| Fire-and-forget Hook | ⭐⭐⭐⭐ 非阻塞捕获的设计模式 |
| Observer-only Agent | ⭐⭐⭐⭐ 安全的 AI 压缩方案 |
| 粒度向量化 | ⭐⭐⭐⭐ 提高向量检索精度的有效策略 |
| 边缘隐私处理 | ⭐⭐⭐⭐ 知识库隐私保护的最佳实践 |

### 8.3 适用场景

- **个人开发知识库**: 自动积累开发经验，跨会话记忆
- **团队知识传递**: 通过导出/导入功能共享知识
- **长期项目记忆**: 大型项目的渐进式知识积累
- **AI 编码质量提升**: 通过上下文注入减少重复错误

---

## 九、安装部署

```bash
# 一键安装（推荐）
npx claude-mem install

# 手动安装
git clone https://github.com/thedotmack/claude-mem.git
cd claude-mem
bun install
bun run build

# 可选: ChromaDB 语义搜索
pip install chromadb
# 或通过 uv: uv pip install chromadb
```

**最低要求**: Node.js 18+ 或 Bun 1.0+

---

## 十、总结

claude-mem 是目前 **Claude Code 知识库建设的最高水平开源项目**。其三层渐进式披露、双存储策略、Observer-only AI 压缩引擎的设计值得任何知识库项目深入学习。58K+ Star 反映了社区的强烈需求。

**推荐等级: ⭐⭐⭐⭐⭐**（强烈推荐）
**优先级: 最高** — 应作为 Godot 落地验证的首选工具
