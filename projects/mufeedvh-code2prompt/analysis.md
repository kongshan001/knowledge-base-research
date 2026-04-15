# 🔧 Code2Prompt 深度调研分析

> 项目地址: https://github.com/mufeedvh/code2prompt
> Star 数: 7,283 (截至 2026-04-16)
> 调研日期: 2026-04-16
> 调研状态: ✅已完成

---

## 一、项目概述

### 定位
Code2Prompt 是一个 Rust 编写的命令行工具，用于将代码库转换为单个 LLM 提示。与 Repomix 类似，但它提供了**交互式 TUI（终端用户界面）**让用户在打包前精确选择要包含的文件，同时支持 Handlebars 模板自定义输出格式。

### 目标用户
- 需要精确控制 AI 上下文的开发者
- 希望自定义输出格式的团队
- 需要高性能代码打包的场景

### 核心价值
1. **交互式文件选择**：TUI 界面允许逐文件选择/排除，精确控制上下文
2. **模板系统**：基于 Handlebars 的灵活模板，支持自定义变量
3. **高性能**：Rust 编写，速度快、内存低
4. **多格式处理器**：支持 CSV、TSV、JSONL、ipynb 等特殊文件格式
5. **Python SDK**：提供 Python 绑定，方便集成到自动化流程

---

## 二、架构分析

### 项目结构（Cargo Workspace）

```
crates/
├── code2prompt/          # 主 CLI 应用
│   ├── src/
│   │   ├── main.rs       # 入口
│   │   ├── args.rs       # CLI 参数解析（clap）
│   │   ├── tui.rs        # TUI 界面（ratatui）
│   │   ├── config.rs     # 配置管理
│   │   ├── model/        # 数据模型
│   │   │   ├── commands.rs
│   │   │   ├── prompt_output.rs
│   │   │   ├── settings.rs
│   │   │   ├── statistics/   # 统计信息
│   │   │   └── template/     # 模板管理
│   │   └── widgets/      # TUI 组件
│   │       ├── file_selection.rs   # 文件选择器
│   │       ├── output.rs           # 输出预览
│   │       ├── settings.rs         # 设置面板
│   │       └── statistics_*        # 统计展示
│   └── tests/
│
├── code2prompt-core/     # 核心库
│   └── src/
│       ├── lib.rs           # 模块入口
│       ├── configuration.rs # 配置定义（Builder 模式）
│       ├── filter.rs        # 文件过滤引擎
│       ├── selection.rs     # 文件选择引擎（优先级规则）
│       ├── template.rs      # Handlebars 模板渲染
│       ├── tokenizer.rs     # Token 计数（tiktoken-rs）
│       ├── sort.rs          # 文件排序（名称/类型/token数/修改时间）
│       ├── git.rs           # Git 集成（diff/log）
│       ├── path.rs          # 路径处理
│       ├── session.rs       # 会话管理
│       ├── util.rs          # 工具函数
│       ├── file_processor/  # 文件处理器
│       │   ├── default.rs   # 默认文本处理
│       │   ├── csv.rs       # CSV 处理
│       │   ├── tsv.rs       # TSV 处理
│       │   ├── jsonl.rs     # JSONL 处理
│       │   └── ipynb.rs     # Jupyter Notebook 处理
│       └── builtin_templates.rs # 内置模板
│
└── code2prompt-python/   # Python SDK
    └── src/
        ├── lib.rs
        └── python.rs     # PyO3 绑定
```

### 核心数据流

```
输入（目录路径）
    ↓
文件遍历 + 过滤（filter.rs）
    │  ├─ include/exclude glob 模式匹配
    │  └─ .gitignore 规则集成
    ↓
TUI 交互式选择（selection.rs）─→ A,A',B,B' 优先级系统
    ↓
文件读取 + 格式处理（file_processor/）
    │  ├─ 文本文件 → 直接读取
    │  ├─ CSV/TSV → 格式化处理
    │  ├─ JSONL → 行解析
    │  └─ ipynb → Notebook 结构提取
    ↓
模板渲染（template.rs）─→ Handlebars 引擎
    │  ├─ 内置模板（default-markdown, markdown, xml 等）
    │  ├─ 自定义模板（用户 .hbs 文件）
    │  └─ 变量注入（代码、路径、扩展名等）
    ↓
输出 → 文件 / stdout / 剪贴板
```

### 设计模式
1. **Builder 模式**：`Code2PromptConfig` 使用 derive_builder，支持链式调用
2. **策略模式**：文件处理器（default, csv, tsv, jsonl, ipynb）按文件类型分派
3. **优先级引擎**：SelectionEngine 实现 A,A',B,B' 系统，支持用户操作覆盖基础过滤
4. **模板方法模式**：Handlebars 模板 + 自定义变量

---

## 三、技术栈

### 语言与框架
- **语言**：Rust（高性能、内存安全）
- **CLI 解析**：clap
- **TUI 框架**：ratatui
- **模板引擎**：Handlebars
- **Token 计数**：tiktoken-rs
- **Python 绑定**：PyO3

### 核心依赖
| 依赖 | 用途 |
|------|------|
| `clap` | CLI 参数解析 |
| `ratatui` | TUI 终端用户界面 |
| `handlebars` | 模板渲染引擎 |
| `tiktoken-rs` | Token 计数（支持 cl100k/o200k/p50k/r50k） |
| `pyO3` | Python SDK 绑定 |
| `ignore` | .gitignore 兼容的文件过滤 |
| `anyhow` | 错误处理 |

### 支持的 Tokenizer
- o200k（GPT-4o）
- cl100k（ChatGPT）
- p50k（Code models）
- p50k_edit（Edit models）
- r50k（GPT-3）

---

## 四、源码分析

### 核心代码路径

#### 1. 选择引擎（selection.rs）
实现了 A,A',B,B' 优先级系统：
- A: 基础 include 模式
- B: 基础 exclude 模式
- A': 用户手动 include 操作（覆盖 B）
- B': 用户手动 exclude 操作（覆盖 A）
- 优先级规则：specific > generic, recent > old
- 使用 HashMap 缓存提升查询性能

#### 2. 文件过滤（filter.rs）
基于 `ignore` crate 的过滤引擎，兼容 .gitignore 规则。

#### 3. 模板系统（template.rs）
- Handlebars 模板引擎注册 `no_escape` 避免代码被转义
- 内置变量：`absolute_code_path`, `source_tree`, `files`, `path`, `code`, `extension`, `no_codeblock`, `git_diff`, `git_log_branch`
- 支持用户自定义变量

#### 4. 文件处理器（file_processor/）
按文件类型分派处理策略：
- `default.rs` — 普通文本文件
- `csv.rs` — CSV 格式化
- `tsv.rs` — TSV 格式化
- `jsonl.rs` — JSON Lines 解析
- `ipynb.rs` — Jupyter Notebook（提取代码单元格和 markdown）

#### 5. TUI 界面
基于 ratatui 的交互式界面：
- 文件树浏览器（可选择/排除文件）
- 实时 token 计数
- 模板选择和编辑器
- 输出预览
- 统计信息展示（按扩展名、token 分布等）

---

## 五、优缺点分析

### 优点（6 条）

1. **交互式精确控制**：TUI 界面允许逐文件选择，这在处理大型代码库时非常重要，可以精确控制哪些文件进入上下文
2. **Rust 高性能**：编译为原生二进制，启动快、内存占用低，适合 CI/CD 和自动化流程
3. **灵活的模板系统**：Handlebars 模板支持自定义输出格式，可适配不同 LLM 的偏好格式
4. **特殊文件格式支持**：对 CSV、TSV、JSONL、Jupyter Notebook 等数据文件有专门处理器
5. **Python SDK**：提供 Python 绑定，方便集成到数据科学和自动化工作流
6. **Token 计数丰富**：支持 5 种 Tiktoken 编码器，覆盖主流模型

### 缺点（4 条）

1. **无 MCP 支持**：不支持 Model Context Protocol，无法直接集成到 Claude Code 的 MCP 生态
2. **无代码压缩**：没有 Tree-sitter AST 压缩等智能压缩功能，所有文件内容原样输出
3. **无安全检查**：没有内置敏感信息检测（密钥、token 等），存在上下文泄露风险
4. **无远程仓库支持**：只能处理本地目录，不支持直接打包 GitHub 仓库

---

## 六、最佳应用场景

1. **精确上下文构建**：需要逐文件控制 AI 上下文内容时，TUI 交互式选择非常实用
2. **批量自动化**：通过 Python SDK 集成到 CI/CD 流程，自动为不同模块生成上下文
3. **数据文件处理**：需要将 CSV、JSONL、Notebook 等数据文件纳入 AI 上下文时
4. **自定义模板输出**：团队有特定的 LLM 提示格式需求时，可自定义 Handlebars 模板
5. **性能敏感场景**：需要快速、低内存占用的代码打包时（Rust 原生优势）

---

## 七、与 Claude Code 集成方式

### 方式一：命令行管道
```bash
# 安装
cargo install code2prompt

# 打包项目并输出到文件
code2prompt /path/to/project --output-file prompt.md

# 在 CLAUDE.md 中引用
echo "项目代码上下文见 prompt.md" >> CLAUDE.md
```

### 方式二：Python SDK
```python
from code2prompt_rs import Code2Prompt

c2p = Code2Prompt("/path/to/project")
c2p.include("**/*.py")
c2p.exclude("**/test_*.py")
output = c2p.generate()
# 将 output 写入 CLAUDE.md 或作为上下文注入
```

### 方式三：TUI 交互
```bash
code2prompt /path/to/project --tui
# 在 TUI 中选择文件 → 生成提示 → 复制到剪贴板
```

> ⚠️ 注意：Code2Prompt 暂不支持 MCP 协议，无法像 Repomix 那样直接作为 MCP Server 集成到 Claude Code。

---

## 八、与 Repomix 对比

| 特性 | Repomix | Code2Prompt |
|------|---------|-------------|
| 语言 | TypeScript | Rust |
| MCP 支持 | ✅ | ❌ |
| TUI 界面 | ❌ | ✅ |
| Tree-sitter 压缩 | ✅ (~70% token 减少) | ❌ |
| 安全检查 | ✅ (secretlint) | ❌ |
| 远程仓库 | ✅ | ❌ |
| 模板系统 | 内置 4 种格式 | Handlebars 自定义 |
| Python SDK | ❌ | ✅ |
| Skill 生成 | ✅ | ❌ |
| 特殊文件格式 | ❌ | ✅ (CSV/TSV/JSONL/ipynb) |
| Token 计数 | Tiktoken | Tiktoken (5种编码器) |

---

## 九、总结与建议

Code2Prompt 在精确文件选择和自定义输出方面有其独特优势，特别是 TUI 界面对开发者体验很好。但作为 Claude Code 知识库的基础工具，其缺少 MCP 支持和代码压缩功能是较大短板。

**建议使用方式**：
1. 在需要**精确控制上下文**时作为 Repomix 的补充工具
2. 利用 Python SDK 集成到自动化工作流
3. 处理数据文件（CSV/Notebook）时使用