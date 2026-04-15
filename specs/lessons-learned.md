# 📝 经验教训与踩坑记录

> 持续更新，记录项目执行过程中遇到的所有问题及解决方案

---

## 通用问题

### 2026-04-16: gh CLI 需要显式设置 HOME 环境变量
- **问题**：在 cron 定时任务中执行 `gh` 命令时报 "not logged in"
- **原因**：`gh` 通过 `$HOME/.config/gh/hosts.yml` 读取认证信息，但 cron 环境中 `HOME` 可能未设置
- **解决**：每个 `gh` 命令前加 `HOME=/root`，或在脚本开头 `export HOME=/root`

### 2026-04-16: GitHub 搜索关键词需要多元化
- **问题**：仅用 "claude code knowledge base" 等精确关键词搜索，结果很少
- **解决**：增加 "code semantic search"、"codebase understanding tool"、"code RAG knowledge" 等广义关键词，发现更多相关项目

### 2026-04-16: 代码打包工具 vs 知识库工具的区别
- **发现**：大多数高 Star 项目是「代码打包工具」（如 Repomix、code2prompt），而非真正的「知识库」工具
- **区别**：
  - 代码打包工具：将代码原样（或压缩后）拼接到上下文中，无语义理解
  - 知识库工具：需要向量索引、语义搜索、增量更新等能力
- **策略**：两类工具都需要调研。打包工具作为基础层，知识库工具作为增强层

---

## 知识库相关

*（待落地验证过程中逐步填充）*

---

## Claude Code 集成相关

### 2026-04-16: Repomix MCP 集成是最成熟的方案
- **发现**：Repomix 原生支持 MCP Server 模式，可直接在 Claude Code 中使用
- **集成方式**：`repomix --mcp` 启动 MCP 服务器，提供 8 个工具
- **最佳实践**：使用 `grep_repomix_output` 进行增量检索，而非一次性加载全部代码

---

## Benchmark 相关

*（待评测过程中逐步填充）*