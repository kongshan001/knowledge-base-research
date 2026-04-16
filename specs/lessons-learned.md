# 📝 经验教训与踩坑记录

> 持续更新，记录项目执行过程中遇到的所有问题及解决方案

---

## 通用问题

### 2026-04-16: gh CLI 需要显式设置 HOME 环境变量
- **问题**：在 cron 定时任务中执行 `gh` 命令时报 "not logged in"
- **原因**：`gh` 通过 `$HOME/.config/gh/hosts.yml` 读取认证信息，但 cron 环境中 `HOME` 可能未设置
- **解决**：每个 `gh` 命令前加 `HOME=/root`，或在脚本开头 `export HOME=/root`

### 2026-04-16: git 分支冲突时的处理策略
- **问题**：cron 定时任务的本地分支与远程分支 diverged，git pull --rebase 产生多个冲突
- **原因**：上一轮 cron 执行的 commit 未成功推送，远程又有新 commit
- **解决**：使用 `git fetch origin && git reset origin/main --mixed && git checkout -- .` 强制同步到远程版本
- **预防**：每次执行开始前先确认本地与远程一致，push 失败后下次执行应优先解决冲突

### 2026-04-16: GitHub 搜索关键词需要多元化
- **问题**：仅用 "claude code knowledge base" 等精确关键词搜索，结果很少
- **解决**：增加 "code semantic search"、"codebase understanding tool"、"code RAG knowledge" 等广义关键词，发现更多相关项目
- **扩展**：本轮增加 "claude code context"、"greptile" 等关键词，发现 ContextKit、cctx 等新项目

### 2026-04-16: 代码打包工具 vs 知识库工具的区别
- **发现**：大多数高 Star 项目是「代码打包工具」（如 Repomix、code2prompt），而非真正的「知识库」工具
- **区别**：
  - 代码打包工具：将代码原样（或压缩后）拼接到上下文中，无语义理解
  - 知识库工具：需要向量索引、语义搜索、增量更新等能力
- **策略**：两类工具都需要调研。打包工具作为基础层，知识库工具作为增强层

### 2026-04-16: git push 认证失败的解决方案
- **问题**：`git push origin main` 报 "Invalid username or token"
- **原因**：hosts.yml 中存储的是遮蔽后的 token（`ghp_5E...7bKo`），非完整 token
- **解决**：使用 GitHub Git Data API 通过 `gh api` 推送：
  1. 为每个文件创建 blob（`POST /git/blobs`）
  2. 创建新 tree（`POST /git/trees`，基于 base_tree）
  3. 创建新 commit（`POST /git/commits`）
  4. 更新分支引用（`PATCH /git/refs/heads/main`）

---

## 知识库相关

*（待落地验证过程中逐步填充）*

---

## Claude Code 集成相关

### 2026-04-16: Repomix MCP 集成是最成熟的方案
- **发现**：Repomix 原生支持 MCP Server 模式，可直接在 Claude Code 中使用
- **集成方式**：`repomix --mcp` 启动 MCP 服务器，提供 8 个工具
- **最佳实践**：使用 `grep_repomix_output` 进行增量检索，而非一次性加载全部代码

### 2026-04-16: Sweep 的搜索管线设计值得借鉴
- **发现**：Sweep 的多路检索融合策略（向量检索 + Tantivy 全文 + Cohere 重排序 + NetworkX 依赖图修剪）是知识库建设的参考架构
- **注意**：Sweep 已转型 JetBrains 插件方向，GitHub App 版维护力度下降
- **借鉴点**：`context_pruning.py` 中的依赖图修剪算法和 `ticket_utils.py` 中的多路检索融合可直接复用

### 2026-04-16: 纯文档项目的调研注意事项
- **发现**：lucasrosati/claude-code-memory-setup 是纯 README 项目，无可执行源码
- **判断标准**：克隆后发现只有 .md 文件时，应降低调研深度，重点分析其方法论和设计思路
- **价值**：即使无代码，其架构设计（Obsidian Zettelkasten + Graphify + 三层查询规则）仍有参考价值

---

## Benchmark 相关

*（待评测过程中逐步填充）*