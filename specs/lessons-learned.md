# 📝 经验教训与踩坑记录

> 持续更新，记录项目执行过程中遇到的所有问题及解决方案

---

## 通用问题

### 2026-04-16: gh CLI 未认证，使用 curl 直接调 GitHub API
- **问题**：`gh search repos` 报 "not logged in"
- **原因**：cron 环境中 `gh` 无认证信息
- **解决**：使用 `curl -s "https://api.github.com/search/repositories?q=QUERY+stars:%3E5000&sort=stars&order=desc&per_page=10"` 直接调 GitHub REST API，无需认证
- **优势**：无需 token，每个 IP 每小时 60 次请求足够调研使用

### 2026-04-16: GitHub Trending 浏览需要 JS 提取
- **问题**：GitHub Trending 页面数据需要 JavaScript 执行才能提取
- **解决**：使用 `browser_navigate` 访问 Trending 页面，然后 `browser_console` 执行 JS 提取项目信息
- **注意**：console 中变量不能重复声明（`let`/`const`），使用块作用域 `{}` 包裹

### 2026-04-16: GitHub 搜索关键词需要多元化
- **问题**：仅用 "claude code knowledge base" 搜索结果很少
- **解决**：增加 "code semantic search"、"codebase understanding tool"、"code RAG knowledge" 等广义关键词
- **成果**：本轮通过多元关键词 + Trending + API 搜索发现了 16 个 ≥5000 Star 的新项目

### 2026-04-16: git 分支冲突时的处理策略
- **问题**：cron 定时任务的本地分支与远程分支 diverged
- **解决**：`git fetch origin && git reset origin/main --mixed && git checkout -- .`
- **预防**：每次执行开始前先确认本地与远程一致

### 2026-04-16: 代码打包工具 vs 知识库工具的区别
- **发现**：大多数高 Star 项目是「代码打包工具」而非「知识库」工具
- **策略**：打包工具作为基础层（Repomix），知识库工具作为增强层（claude-mem），向量数据库作为存储层

---

## 知识库架构设计

### 2026-04-16: 三层渐进式披露是知识库检索的最佳范式
- **来源**：claude-mem 源码分析
- **核心思想**：search（索引层 ~50-100 tok/结果）→ timeline（上下文层）→ get_observations（详情层 ~500-1000 tok/观察）
- **效果**：比传统 RAG 节省 50-75% Token，因为只在验证后才加载完整数据
- **实践建议**：任何知识库项目都应采用此范式，避免一开始就返回大量完整文档

### 2026-04-16: 双存储策略（SQL + Vector）是最优解
- **来源**：claude-mem + bloop 共同验证
- **claude-mem 方案**：SQLite (结构化查询+FTS5) + ChromaDB (向量语义)，可独立降级
- **bloop 方案**：Tantivy (全文BM25) + Qdrant (向量)，通过 RRF 合并
- **结论**：结构化查询（过滤、排序）用 SQL/倒排索引，语义搜索用向量 DB，两者互补
- **关键**：必须有降级策略（ChromaDB 不可用时回退到 SQLite FTS5）

### 2026-04-16: Tree-sitter 感知分块远优于朴素分割
- **来源**：bloop 源码分析
- **方法**：用 Tree-sitter 解析 AST → 按语法节点边界分块 → 50-256 tokens/chunk
- **优势**：每个分块包含完整的函数/类/方法，语义完整
- **对比**：朴素按行或按 token 数分割会产生截断的代码片段，降低检索质量

### 2026-04-16: RRF (Reciprocal Rank Fusion) 是混合搜索合并的简洁方案
- **来源**：bloop 源码分析
- **公式**：`score = 1/(k + rank)`，k=60
- **优势**：无需归一化分数，简单有效
- **适用**：BM25 + 向量搜索的结果合并

### 2026-04-16: 粒度向量化提高检索精度
- **来源**：claude-mem 源码分析
- **方法**：不是将整条观察作为一个向量文档，而是每个语义字段（narrative, fact, concept）分别向量化
- **优势**：精确匹配到具体字段，而非整条记录的模糊匹配
- **代价**：向量文档数量增加，但 ChromaDB 的过滤能力可以补偿

### 2026-04-16: Observer-only Agent 是安全的 AI 压缩方案
- **来源**：claude-mem 源码分析
- **方法**：AI Agent 禁止执行任何工具（Bash, Read, Write 等全部禁用），只分析输入并输出结构化 XML
- **优势**：完全安全可控，不会产生副作用
- **适用场景**：任何需要 AI 处理用户数据的场景

### 2026-04-16: HyDE (假设文档嵌入) 提高低资源查询召回率
- **来源**：bloop 源码分析
- **方法**：当语义搜索结果不足时，用 LLM 生成假设代码片段，重新嵌入后作为补充查询
- **适用**：查询过于抽象或模糊时的补救措施
- **代价**：额外 LLM 调用成本

---

## Claude Code 集成相关

### 2026-04-16: claude-mem 是最成熟的 Claude Code 知识库集成方案
- **集成方式**：
  - Hooks: 5 个生命周期钩子（SessionStart/UserPromptSubmit/PostToolUse/Stop/SessionEnd）
  - MCP: 4 个工具（__IMPORTANT/search/timeline/get_observations）
  - Context Injection: SessionStart 时通过 `additionalContext` 静默注入
- **最佳实践**：三层渐进式披露通过 MCP 工具设计强制执行，而非依赖 Prompt
- **安装**：`npx claude-mem install` 一键安装

### 2026-04-16: MCP + Hooks 双集成是 Claude Code 扩展的最佳模式
- **发现**：claude-mem 同时使用 Hooks（数据捕获）和 MCP Server（数据检索），形成完整闭环
- **Hooks 负责**：自动捕获（PostToolUse）、上下文注入（SessionStart）、摘要生成（Stop）
- **MCP 负责**：按需检索（search/timeline/get_observations）
- **设计原则**：捕获自动化（用户无感知），检索主动化（用户按需查询）

### 2026-04-16: Fire-and-forget 是 Hook→Worker 通信的最佳模式
- **来源**：claude-mem
- **方法**：Hook 发送 HTTP POST，2s 超时，不等待响应
- **优势**：绝不阻塞 IDE，用户体验无影响
- **代价**：可能丢失少量数据（网络异常时），但知识库容错性强

---

## Benchmark 相关

*（待评测过程中逐步填充）*

---

## 工具使用技巧

### 2026-04-16: delegate_task 并行分析多个项目
- **方法**：使用 `delegate_task(tasks=[...])` 并行启动 2 个子 Agent 分别分析不同项目
- **优势**：节省时间，两个子 Agent 独立运行
- **限制**：最多 3 个并行任务；子 Agent 无上下文，需要通过 context 参数传递所有信息

### 2026-04-16: GitHub API 分页与限制
- **限制**：未认证 API 每 IP 每小时 60 次请求
- **策略**：每次调研最多 10-15 次搜索请求，远低于限制
- **分页**：`per_page` 参数最大 100，通常 10-30 足够
